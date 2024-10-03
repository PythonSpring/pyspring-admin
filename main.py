from py_spring_core import PySpringApplication
from py_spring_model import provide_py_spring_model
from py_spring_admin import provide_py_spring_admin, provide_test_tables


def main():
    app = PySpringApplication(
        "./app-config.json",
        entity_providers=[provide_py_spring_model(),provide_py_spring_admin(), provide_test_tables()],
    )
    app.run()


if __name__ == "__main__":
    main()
