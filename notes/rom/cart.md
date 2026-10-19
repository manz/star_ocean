# Cart

- 6 MB, sha1 `a616ee3466256482bc0adc11f1fda7c30e66ef8d`.
- S-DD1: header map `$32`, cart type `$45`, SRAM 8 KB → board `SHVC-LN3B-01`.
- `00-3F:8000-FFFF` LoROM.
- `C0-FF` through the S-DD1 MMC: `$4804-$4807` select the 1 MB ROM page for `C0/D0/E0/F0`
  (default 0-3 → first 4 MB). Data above 4 MB needs a bank switch: find who writes `$4804-7`.
- Example: `FF:0000` → ROM `0x3F0000`.
