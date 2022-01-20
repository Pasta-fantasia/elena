import json

def read_state(p_robot_filename):
    fp = open(p_robot_filename, 'r')
    elena = json.load(fp)
    fp.close()
    return elena


def save_state(p_robot_filename, p_elena):
    fp = open(p_robot_filename, 'w')
    json.dump(p_elena, fp)
    fp.close()