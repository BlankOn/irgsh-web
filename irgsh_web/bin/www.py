from django.core.management import execute_manager

def main():
    from irgsh_web import wwwsettings
    execute_manager(wwwsettings)

if __name__ == '__main__':
    main()
