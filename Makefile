# Define the default target
.PHONY: run

# Target to run the main script
run:
	@echo "Loading environment variables and running main.py..."
	@if [ -f .env ]; then \
		set -a; \
		source .env; \
		set +a; \
	else \
		echo ".env file not found!"; \
		exit 1; \
	fi
	@if [ -d .venv ]; then \
		source .venv/bin/activate; \
	else \
		echo "Python virtual environment not found!"; \
		exit 1; \
	fi
	PYTHONPATH=$(PWD) python scripts/main.py

# Target to install dependencies
install:
	@echo "Installing dependencies..."
	@if [ -d .venv ]; then \
		source .venv/bin/activate && pip install -r requirements.txt; \
	else \
		echo "Python virtual environment not found!"; \
		exit 1; \
	fi

# Target to clean up (example)
clean:
	@echo "Cleaning up..."
	@rm -rf __pycache__ outputs/*