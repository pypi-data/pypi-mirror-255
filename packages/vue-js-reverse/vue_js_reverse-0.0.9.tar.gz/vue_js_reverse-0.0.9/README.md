VUE JS Reverse
--------------

**Vue url handling for Django that doesn’t hurt.**


Overview
--------

Django Vue Reverse (a fork of Django Js Reverse) is a small django app that makes url handling of
named urls (https://docs.djangoproject.com/en/dev/topics/http/urls/#naming-url-patterns) in javascript easy and non-annoying..

You can retrieve a named url:

urls.py:

    path('company/update/company_id/<int:company_id>/', main.update_company, name='update_company')

in javascript like:

    this.$urls.update_company(12)

Result:

    company/update/company_id/12/


Requirements
------------

python 3.6+


Installation
------------

Install using ``pip`` …

    pip install vue-js-reverse

... or clone the project from github.

    git clone https://github.com/miklagard/vue-js-reverse

Add ``'vue_js_reverse'`` to your ``INSTALLED_APPS`` setting.

    INSTALLED_APPS = (
        ...
        'vue_js_reverse',
    )

Add library variables to settings.py file.

    VUE_PLUGINS_DIR = os.path.join(settings.BASE_DIR, 'vue_frontend', 'src', 'plugins')
    VUE_REVERSE_URL_PLUGIN = 'Urls.js'

Vue main.js
------------------

     import Url from "@/plugins/Url"
     Vue.use(Url)


Usage as static file
--------------------

First generate static file by

    ./manage.py vue_js_reverse

If you change some urls or add an app and want to update the reverse.js file,
run the command again.

After this add the file to your template


License
-------

MIT 
https://raw.githubusercontent.com/miklagard/vue-js-reverse/master/LICENSE


Contact
-------

cem.yildiz@ya.ru

--------------

Enjoy!
