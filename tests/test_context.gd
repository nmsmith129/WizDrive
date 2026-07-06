class_name TestContext
extends RefCounted

var passed := 0
var failed := 0

func check(label: String, ok: bool) -> void:
    if ok: passed += 1
    else:
        failed += 1
        print("FAIL: ", label)
    return