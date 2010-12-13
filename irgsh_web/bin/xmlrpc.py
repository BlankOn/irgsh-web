from django.core.management import execute_manager

def main():
    from irgsh_web import xmlrpcsettings
    execute_manager(xmlrpcsettings)

if __name__ == '__main__':
    main()
