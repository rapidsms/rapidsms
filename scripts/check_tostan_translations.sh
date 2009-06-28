for i in 'deb' 'dyu' 'en' 'fr' 'pul' 'wol'
do
     python check_translation.py ../apps/smsforum/locale/$i/LC_MESSAGES/django.po
done
