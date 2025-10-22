from backend.utils.responses import success, error


def test_success_minimal():
    resp = success()
    assert resp["status"] == "success"
    assert resp["message"] == "ok"
    assert "data" not in resp


def test_success_with_data_and_extra():
    data = {"a": 1}
    resp = success(data, message="done", extra=True)
    assert resp["status"] == "success"
    assert resp["message"] == "done"
    assert resp["data"] == data
    assert resp["extra"] is True


def test_error_minimal():
    resp = error("bad")
    assert resp["status"] == "error"
    assert resp["message"] == "bad"
    assert "code" not in resp
    assert "details" not in resp


def test_error_with_code_and_details_and_extra():
    resp = error("bad", code="X", details={"d": 1}, foo="bar")
    assert resp["status"] == "error"
    assert resp["message"] == "bad"
    assert resp["code"] == "X"
    assert resp["details"] == {"d": 1}
    assert resp["foo"] == "bar"
