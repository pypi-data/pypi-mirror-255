from prefref import *

# setup data class for my app's config
@dataclass
class MyOptions(Config_Options):
  do_thing: Config_Option
  username: Config_Option
  password: Config_Option

# create instance of my app's config
my_options = MyOptions(
    do_thing=Config_Option(
      name='do_thing',
      default_value=False,
      value_type=bool,
      help_text='whether or not to do thing'
    ),
    username=Config_Option(
      name='username',
      value_type=str,
      arg_short_key='-u',
      arg_key='username',
      help_text='username for login',
      required=True,
      env_var='MY_USERNAME'
    ),
    password=Config_Option(
      name='password',
      value_type=str,
      help_text='password for login',
      required=True,
      is_secret=True
    )
  )

# initialize app config using my options
# my_config = Config(options=my_options, app_name='PrefRef', app_desc='Fusing Config Options!')
