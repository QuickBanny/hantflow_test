import yaml
import os


def parse_config_data():
    try:
        path_config_files = os.getcwd() + '/config.yaml'
        with open(path_config_files, encoding='utf8') as c:
            config_data = yaml.load(c, Loader=yaml.FullLoader)
        return config_data
    except Exception as es:
        print(es)


def main():
   pass


if __name__ == '__main__':
    main()