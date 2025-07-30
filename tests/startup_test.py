def startup_test():
    try:
        import app.main
    except Exception as e:
        assert False, f"Ошибка при импорте main.py: {e}"