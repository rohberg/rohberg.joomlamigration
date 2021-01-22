## Migration of a MySQL based CMS to Plone

#plone #plone-addon #sql #transmogrifier #joomla


Run with
```
/bin/migrate --pipeline=path-to-pipeline/joomlamysql.cfg --zcml=transmogrify.sqlalchemy sqlalchemysource:dsn=mysql://lisa:lisaspassword@ip-host:3306/dbname
```

See more infos about how to use and customize migration with Mr.Migrator on 
https://github.com/collective/mr.migrator#build-your-own-pipeline


Author: Katja Süss, Rohberg

