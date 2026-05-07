# Variables - Pointing directly to the binaries inside the venv
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

# Target to install dependencies
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Target to run the application
run:
	$(STREAMLIT) run app/app.py

# Target to clean temporary files
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -delete