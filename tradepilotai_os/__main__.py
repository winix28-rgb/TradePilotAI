from .application import Application


def main():

    app = Application()

    try:

        app.run()

    finally:

        app.shutdown()


if __name__ == "__main__":

    main()
