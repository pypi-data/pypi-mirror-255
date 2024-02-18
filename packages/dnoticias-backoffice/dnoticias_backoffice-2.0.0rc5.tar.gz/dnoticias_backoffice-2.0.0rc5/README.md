=====
dnoticias_backoffice
=====
This package contains all the utilities/components/templates used in the dnoticias.pt backoffices.
Our objective is to have in one place the most used HTML components/layouts, this will standardize
all the sites and will allow more easy theme/components updates.


## Settings

1) Add the following variables to the project settings
```py
# Base full URL (like https://subdomain.example.com)
BASE_URL = ""
# Verbose site name (like Edição, Assinaturas, etc)
SITE_NAME = ""
```

2) Add the context processor in your settings and the slippers builtin (to avoid 
writing {% load slippers %} in every template where we use components).
```py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'dnoticias_backoffice.context_processors.backoffice',  # <-
            ],
            "builtins": ["slippers.templatetags.slippers"],  # <-
        },
    },
]
```

3) Add 'slippers' and 'dnoticias_backoffice' into your installed apps
```py
INSTALLED_APPS = [
    ...
    'dnoticias_backoffice',
    'slippers',
    ...
]
```


## How to load custom components
This project already has his own components, to load custom components without crashing the project
you just need to create a py file (e.g: components.py) in the project folder (where the settings.py
file is located at), create a function called e.g: load_custom_components(), inside this function
you will call the register_components function (https://mitchel.me/slippers/docs/registering-components/)
and finally, go to your apps.py file, locate or create the def ready() function and then import and
add the load_custom_components() function call.


## How to add/update/remove menu items
Create a menu.py file inside the project folder (where the settings.py file is located at), create
a function called e.g: load_menu(), inside this function you need to call register_menu_item function
imported from `dnoticias_backoffice.menu`. When you finally defined all the menu items you need to
import and call the load_menu() function into the def ready() function on the apps.py file (just 
like we call the custom components)


## Project templates structure
`templates/components` includes all the slipper components used along the backoffice.
`templates/backoffice` includes the masters templates and includes.
