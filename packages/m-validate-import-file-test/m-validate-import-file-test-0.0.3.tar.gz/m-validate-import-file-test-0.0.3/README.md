##  Thư viện kiểm tra file type.

### Cài đặt:

```bash
 $ pip3 install m-validate-import-file
 ```

### Sử dụng
```python
from mobio.libs.validate_import_file.validate import ValidateImportFile

result_validate = ValidateImportFile(
    number_row_limit=300000,
    capacity_limit=10485760 # 10MB
).file_upload(
    file=file
)

##
1. Lỗi định dạng file không đúng
result_validate = {
    "status": False,
    "reason": "fail_validate_file_type",
}

2. Lỗi file có số dòng vượt quá limit

result_validate = {
    "status": False,
    "reason": "fail_validate_file_number_row",
}

3. Lỗi file có dung lượng vượt quá config

result_validate = {
    "status": False,
    "reason": "fail_validate_file_number_row",
}



```
