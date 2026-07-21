"""
Ağda pytest kurulamadığı için (offline sandbox) tests/test_actp.py'yi
gerçek pytest olmadan çalıştıran minimal bir koşucu.
Sadece düz `assert` kullanan, fixture/parametrize/raises KULLANMAYAN
pytest-style test dosyaları için yeterlidir.
"""
import inspect
import sys
import traceback
import types


fake_pytest = types.ModuleType("pytest")
fake_pytest.main = lambda *a, **k: None
sys.modules["pytest"] = fake_pytest

sys.path.insert(0, "tests")
import test_actp  # noqa: E402


passed, failed, errors = 0, 0, []

for name in dir(test_actp):
    obj = getattr(test_actp, name)
    if inspect.isclass(obj) and name.startswith("Test"):
        instance = obj()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                method = getattr(instance, method_name)
                try:
                    method()
                    passed += 1
                    print(f"PASS  {name}.{method_name}")
                except Exception as e:  # noqa: BLE001
                    failed += 1
                    tb = traceback.format_exc()
                    errors.append((f"{name}.{method_name}", tb))
                    print(f"FAIL  {name}.{method_name}: {e}")

print("\n" + "=" * 70)
print(f"Toplam: {passed + failed}  |  Geçen: {passed}  |  Başarısız: {failed}")
print("=" * 70)

if errors:
    print("\n--- HATA DETAYLARI ---")
    for test_name, tb in errors:
        print(f"\n{test_name}:\n{tb}")

sys.exit(1 if failed else 0)
