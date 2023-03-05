import os
import json
import datetime


def get_config():
    try:
        path = os.path.join(os.getcwd(), 'config.json')
        if os.path.isfile(path):
            with open(path) as f:
                config = json.load(f)
                for k in config.keys():
                    if config[k]['last_blog_date'] and isinstance(config[k]['last_blog_date'], str):
                        config[k]['last_blog_date'] = datetime.datetime.strptime(config[k]['last_blog_date'],
                                                                                 "%Y-%m-%d %H:%M:%S")
                return config
        else:
            return {}
    except Exception as e:
        return {}


def set_config(config: dict):
    path = os.path.join(os.getcwd(), 'config.json')

    for k in config.keys():
        if config[k]['last_blog_date'] and isinstance(config[k]['last_blog_date'], datetime.datetime):
            config[k]['last_blog_date'] = config[k]['last_blog_date'].strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as outfile:
        # Write the dictionary to the file as formatted JSON
        json.dump(config, outfile, indent=4)
