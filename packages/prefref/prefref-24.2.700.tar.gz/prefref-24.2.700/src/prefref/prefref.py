import argparse, copy, json, logging, os, sys, typing
from enum import Enum
from dataclasses import dataclass
from prefref.exceptions import *
from secret_agent import SecretAgent as secrets

# allows option to supply a custom logger
class _Config_Logger_:

  logger: 'typing.any' = None

  def __init__(self, logger: 'typing.any' = None, use_default_logger: bool = True) -> None:

    # use the supplied logger, a default logger, or no logging... depending on options provided
    self.logger = logger if logger else logging.getLogger('prefref') if use_default_logger else None

  def debug(self, msg):
    if self.logger:
      self.logger.debug(msg)

  def info(self, msg):
    if self.logger:
      self.logger.info(msg)

  def error(self, msg):
    if self.logger:
      self.logger.error(msg)

  def critical(self, msg):
    if self.logger:
      self.logger.critical(msg)

# config options you'd like to support
class Config_Provider(Enum):
  ARG = 0
  ENV = 1
  JSON = 2

# config option to define an option to support
@dataclass
class Config_Option:

  # name of the config option, used as the key for this setting
  name: str

  # value type (i.e. str, bool, 'typing.any')
  value_type: type

  # default value
  default_value: 'typing.any' = None

  # value of option, do not set explicitly, this is set during
  # init of the Config class
  value: 'typing.any' = None

  # short key for arg parse (i.e. '-u')
  arg_short_key: str = None

  # key for arg parse (i.e. --username), set to self.name if not provided
  arg_key: str = None

  # help text for arg parse, printed if console app executed with '--help'
  help_text: str = None

  # environment variable to search for, is null and not used if not provided
  env_var: str = None

  # whether this value must be encrypted
  is_secret: bool = False

  # whether this is required, if True and missing the app will exit(1)
  required: bool = False

  # whether this value is an argument flag (cannot be passed with a 'true'/'false' value)
  # flags cannot be stored in config files
  is_flag: bool = False

  # if true, do not parse console arguments for this option
  no_arg_parse: bool = False

  # if true, do not handle in config file(s)
  no_file: bool = False

  # if true, do not check for environment variables for this value
  # environment variables only checked if 'self.env_var' is set
  no_env: bool = False

# the class containing your Config_Option(s) to be supplied to Config
@dataclass
class Config_Options:

  @property
  def restricted_option_names(self) -> list[str]:
    return ['required', 'help']

  # validate Config_Option properties and values
  def __post_init__(self) -> None:

    # add a config_filepath if needed, defaulted to './config.json'
    if any(not o.no_file for o in self.__dict__.values()) and not 'config_filepath' in self.__dict__:
      self.config_filepath = Config_Option(
        name='config_filepath',
        value_type=str,
        default_value='./config.json',
        help_text='filepath for json config file'
      )

    # deny restricted option names (i.e. 'required' and 'help')
    for r in self.restricted_option_names:
      if r in self.__dict__:
        option: Config_Option = self.__dict__[r]
        if not option.no_arg_parse and (option.arg_key == None or option.arg_key == option.name):
          raise Exception(f'Cannot use restricted Config_Option "{option.name}" as an argument, \
                          either set "arg_key" to another value or disallow use as a commandline \
                          argument by setting "no_arg_parse" to True.')

    # create a key if we have secrets and don't have a key
    have_a_secret = any(o.is_secret for o in self.__dict__.values())
    if have_a_secret and not 'key' in self.__dict__:
      need_key = False
      for key in self.__dict__:
        if self.__dict__[key].is_secret:
          need_key = True

      if need_key:
        self.key = Config_Option(
          name='key',
          value_type=bytes,
          default_value=secrets.generateKey()
        )

    # set config_option properties as needed
    for key in self.__dict__:
      option: Config_Option = self.__dict__[key]

      # flags cannot be stored in file and must be bool type
      if option.is_flag:
        option.value_type = bool
        option.no_file = True

      # bool's should have a default value of 'False' if set to 'None'
      if bool is option.value_type and None is option.default_value:
        option.default_value = False

      # set the arg_key to the name if it's not set
      if not option.no_arg_parse and not option.arg_key:
        option.arg_key = option.name

  # get a config option by supplying the name
  def get_option(self, name) -> Config_Option:
    if name in self.__dict__:
      return self.__dict__[name]
    else:
      raise PrefRefOptionNotFound('Config option not found!')
  
  # get a config option value by supplying the name
  def get_value(self, name) -> Config_Option:
    return self.get_option(name=name).value


class Config:

  # options
  options: Config_Options

  # config file
  config_filepath: str

  # logger
  logger = None

  # config providers
  providers: list[Config_Provider] = [Config_Provider.ARG, Config_Provider.ENV, Config_Provider.JSON]


  # default constructor
  def __init__(self, options: Config_Options, app_name: str, app_desc: str, config_filepath: str = './config.json', logger = None, providers: list[Config_Provider] = [Config_Provider.ARG, Config_Provider.ENV, Config_Provider.JSON], unknown_args_fatal: bool = False, reduce_options_to_key_value: bool = True) -> None:
    self.options = options
    self.app_name = app_name
    self.app_desc = app_desc
    self.config_filepath = config_filepath
    self.logger = _Config_Logger_(logger=logger)
    self.providers = providers
    self.unknown_console_args = []

    self._config_options_: Config_Options = options
    self._json_values_: dict = {}
    self._env_values_: dict = {}
    self._arg_values_: dict = {}

    # validate provider options
    pass

    self.logger.debug(f'Loading configuration')

    # read in default values
    for key in self.options.__dict__:
      self.options.__dict__[key].value = self.options.__dict__[key].default_value


    # json
    if Config_Provider.JSON in self.providers:
      self.logger.debug(f'Loading JSON file: {self.options.config_filepath.value}')
      self._json_values_ = self.initial_json_handler(config_filepath=self.options.config_filepath.value, options=self.options)
      for key in self._json_values_:
        if key in self.options.__dict__:
          self.options.__dict__[key].value = self._json_values_[key]


    # read in environment variables
    if Config_Provider.ENV in self.providers:
      self.logger.debug(f'Loading environment variables')
      for key in self.options.__dict__:
        option = self.options.__dict__[key]

        # if we have a defined environment variable for this option and are supporting environment variables for it
        if option.env_var and not option.no_env:

          # if the option is in the environment variable dictionary
          if option.env_var in os.environ:

            self.logger.debug(f'Found environment variable: {option.env_var}')

            # handle bool types differently to support 'is_flag' boolean types
            if bool == option.value_type:
              if option.is_flag or None is os.environ[option.env_var] or '' is os.environ[option.env_var]:
                self.options.__dict__[key].value = True
                self._env_values_[key] = True
              else:
                self.options.__dict__[key].value = "true" == os.environ[option.env_var].lower()
                self._env_values_[key] = "true" == os.environ[option.env_var].lower()

            # cast ints and floats as such
            elif int == option.value_type:
              self.options.__dict__[key].value = int(os.environ[option.env_var])
              self._env_values_[key] = int(os.environ[option.env_var])
            elif float == option.value_type:
              self.options.__dict__[key].value = float(os.environ[option.env_var])
              self._env_values_[key] = float(os.environ[option.env_var])

            # strings
            else:
              self.options.__dict__[key].value = os.environ[option.env_var]
              self._env_values_[key] = os.environ[option.env_var]


    # run argparse to capture console arguments
    if Config_Provider.ARG in self.providers:
      self.logger.debug(f'Loading argument parser')
      parser = argparse.ArgumentParser(description=f'{self.app_name} - {self.app_desc}')
      parser.add_argument('--required', action='store_true', dest='required', 
                          default=False, help='print out the list of required arguments')
      for key in self.options.__dict__:
        if not self.options.__dict__[key].no_arg_parse:
          parser = self.add_parser_arg(parser=parser, option=self.options.__dict__[key])
      self._arg_values_, self.unknown_console_args = parser.parse_known_args()
      for arg in self.unknown_console_args:
        self.logger.info(f'Found unknown argument: {arg}')

      # ensure any bool options are set to bool and not a string value
      for key in self._arg_values_.__dict__:
        if key not in self.options.__dict__:
          continue

        option: Config_Option = self.options.__dict__[key]
        arg_value = self._arg_values_.__dict__[key]
        if bool == option.value_type and not option.is_flag and (arg_value is None or isinstance(arg_value, str)):
          self._arg_values_.__dict__[key] = True if arg_value is None else "true" == arg_value.lower()

      # if user supplied '--required' then print required options then exit application
      if self._arg_values_.required:
        print(f'Required arguments are as follows:')
        for item in self.get_required_args():
          print(f'    * {item}')
        sys.exit(0)

      if unknown_args_fatal:
        raise PrefRefUnknownArgument('Unknown arguments provided, please see --help for more info!')
    
      # apply found arguments
      for key in self._arg_values_.__dict__:
        if key in self.options.__dict__:
          self.options.__dict__[key].value = self._arg_values_.__dict__[key]
 
    # handle secret values
    enc_key = None
    for key in self.options.__dict__:
      config_option = self.options.__dict__[key]

      if config_option.is_secret:
        if not enc_key:
          self.logger.debug(f'Encrypting secrets')
          if not 'key' in self.options.__dict__:
            self.options.__dict__['key'].value = str(secrets.generateKey())
          enc_key = self.options.__dict__['key'].value

        # encrypt value
        if config_option.value and not isinstance(config_option.value, bytes):
          config_option.value = secrets.encryptWithKey(key=enc_key, data=config_option.value)

    # update the json config
    if Config_Provider.JSON in self.providers:
      self.logger.debug(f'Updating JSON file')
      self.create_json_config(options=self.options)
      self.logger.debug(json.dumps(json.load(open(self.config_filepath))))

    # fail if missing required options
    missing = self.get_missing_args()
    for item in missing:
      self.logger.error(f'Missing required argument: {item}')

    if len(missing) > 0:
      raise PrefRefMissingRequiredOption('Missing required config items, see --required for more info.')

    self._config_options_ = copy.deepcopy(self.options)
    if reduce_options_to_key_value:
      for key in self.options.__dict__:
        self.options.__dict__[key] = self.options.__dict__[key].value


  # handle a json file while initializing Config
  def initial_json_handler(self, config_filepath: str, options: Config_Options) -> dict:
    if os.path.exists(path=config_filepath):
      return self.read_json_config()
    else:
      return self.create_json_config(options=options)
  

  # read the json file
  def read_json_config(self) -> dict:
    self.logger.debug(f'Reading JSON file: {self.options.config_filepath.value}')
    config_json = open(self.config_filepath)
    if config_json:
      json_content = json.load(config_json)
      for key in json_content:
        value = json_content[key]
        if isinstance(value, str) and value.startswith('b"'):
          value = value.lstrip('b"').rstrip('"')
          value = bytes(value, 'utf-8')
          json_content[key] = value
      return json_content
    return {}


  # create a new json file
  def create_json_config(self, options: Config_Options) -> dict:
    content: dict = {}
    for key in options.__dict__:
      option = options.__dict__[key]
      if not option.no_file:
        content[key] = option.value
    self.write_json_config(content=content)
    return self.read_json_config()


  # write values to json file, converting some values for proper storage
  def write_json_config(self, content: dict = {}) -> dict:
    self.logger.debug(f'Writing JSON file: {self.options.config_filepath.value}')
    json_content = {}
    for key in content:
      value = content[key]
      if isinstance(value, bytes):
        json_content[key] = 'b"' + value.decode('utf8').replace("'", '"') + '"'
      elif isinstance(value, type(None)):
        json_content[key] = None
      elif not isinstance(value, str) and \
           not isinstance(value, int) and \
           not isinstance(value, bool) and \
           not isinstance(value, float):
        json_content[key] = str(value)
      else:
        json_content[key] = value
    with open(file=self.config_filepath, mode='w') as f:
      f.write(json.dumps(json_content, indent=4))
    return json_content

  def update_json_config(self, key: str, value: 'typing.any') -> dict:
    self.logger.debug(f'Updating JSON file: {self.options.config_filepath.value}')
    self.logger.debug(f'{key} = {value}')
    json_content = self.read_json_config()
    json_content[key] = value
    return self.write_json_config(content=json_content)


  # generate dynamic argparse
  def add_parser_arg(self, parser: argparse.ArgumentParser, option: Config_Option) -> argparse.ArgumentParser:
    if bool == option.value_type and option.is_flag:
      if option.arg_short_key:
        parser.add_argument(option.arg_short_key, f'--{option.arg_key}', action='store_true', dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
      else:
        parser.add_argument(f'--{option.arg_key}', action='store_true', dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
    
    elif int == option.value_type:
      if option.arg_short_key:
        parser.add_argument(option.arg_short_key, f'--{option.arg_key}', nargs='?', type=int, dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
      else:
        parser.add_argument(f'--{option.arg_key}', nargs='?', type=int, dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
    else: # string or bool as not flag
      if option.arg_short_key:
        parser.add_argument(option.arg_short_key, f'--{option.arg_key}', nargs='?', type=str, dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
      else:
        parser.add_argument(f'--{option.arg_key}', nargs='?', type=str, dest=option.name, 
                            default=option.value,
                            help=f'{option.help_text}{" (default: " + str(option.default_value) + ")" if option.default_value else ""}')
    
    return parser
  

  # returns list of required args
  def get_required_args(self) -> list[str]:
    required = []
    for key in self.options.__dict__:
      option = self.options.__dict__[key]
      if option.required:
        required.append(option.name)

    return required


  # returns any missing required args
  def get_missing_args(self) -> list[str]:
    missing = []
    for key in self.options.__dict__:
      option = self.options.__dict__[key]
      if option.required and not option.value:
        missing.append(option.name)

    return missing
  

  # encrypt with password
  def encrypt_with_password(self, option_name: str, password: str, update_value_in_config: bool = False) -> bytes:
    option = self.options.__dict__[option_name]
    is_config_option = isinstance(option, Config_Option)

    value = secrets.encryptDataWithPassword(password=password, data=option.value if is_config_option else option)
    if update_value_in_config:
      if is_config_option:
        self.options.__dict__[option_name].value = value
      else:
        self.options.__dict__[option_name] = value

    return value


  # decrypt with password
  def decrypt_with_password(self, option_name: str, password: str, update_value_in_config: bool = False) -> bytes:
    option = self.options.__dict__[option_name]
    enc_key = secrets.generateKeyFromPassword(password=password)
    is_config_option = isinstance(option, Config_Option)

    value = secrets.decryptDataWithPassword(key=enc_key, data=option.value if is_config_option else option)
    if update_value_in_config:
      if is_config_option:
        self.options.__dict__[option_name].value = value
      else:
        self.options.__dict__[option_name] = value

    return value
  

  # decrypt with shared key
  def decrypt(self, option_name: str = None, option_value: bytes = None) -> 'typing.any':
    if option_name:
      enc_value = self.options.__dict__[option_name] if not isinstance(self.options.__dict__[option_name], Config_Option) else self.options.__dict__[option_name].value
    else:
      enc_value = option_value
    enc_key = self.options.__dict__['key'] if not isinstance(self.options.__dict__['key'], Config_Option) else self.options.__dict__['key'].value
    return secrets.decryptWithKey(key=enc_key, data=enc_value)
