from sqlalchemy import create_engine

engine = create_engine('postgresql://medbot:3285@localhost/medbot', echo=True)

def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    print_hi('PyCharm')
