import utils.gui
import sys
def main():
    print("Hello from handwrite!")
    # Initialize the GUI
    app = utils.gui.QApplication(sys.argv)
    gui = utils.gui.HandwritingGUI()
    gui.show()
    # Execute the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
