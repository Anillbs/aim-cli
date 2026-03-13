# AIM CLI — Command-Line Interface

**AIM Security DAST** tarama motorunu terminalden ve CI/CD pipeline'larından tetikleyen thin-client CLI aracı.

## Hızlı Başlangıç

```bash
pip install aim-cli

aim auth login
aim scan start 42 --profile standard --wait
aim vulns list --scan 187 --severity critical,high
```

## CI/CD Entegrasyonu

```yaml
- name: DAST Scan
  env:
    AIM_API_KEY: ${{ secrets.AIM_API_KEY }}
  run: |
    pip install aim-cli
    aim scan start ${{ vars.SITE_ID }} --wait --fail-on high --format sarif --output results.sarif
```

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `aim auth login` | API token ile giriş |
| `aim scan start` | Tarama başlat |
| `aim scan status` | Tarama durumu |
| `aim vulns list` | Zafiyetleri listele |
| `aim vulns export` | SARIF/JSON/CSV export |
| `aim config show` | Yapılandırmayı göster |
| `aim doctor` | Ortam teşhisi |

## Lisans

Proprietary — AIM Security
