ifeq ($(OS), Windows_NT)
init:
	@pip install -r requirements.txt

run_user:
	@uvicorn main:user_app --port 8000 --reload

run_note:
	@uvicorn main:note_app --port 8001 --reload

run_label:
	@uvicorn main:label_app --port 8002 --reload
endif