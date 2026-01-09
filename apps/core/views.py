import pandas as pd
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import DaneOperator1
from django.contrib.gis.geos import Point
import pandas.api.types as pd_types


def parse_datetime(val):
    """Bezpieczne parsowanie z timezone-aware"""
    if pd_types.is_scalar(val) and pd.notna(val) and str(val).strip():
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return timezone.make_aware(dt)
    return None


def parse_numeric(val):
    """Bezpieczne parsowanie liczb"""
    if pd.notna(val):
        return pd.to_numeric(val, errors='coerce')
    return None


def operator1_upload(request):
    if request.method == 'POST':
        plik = request.FILES.get('plik')
        if plik and plik.name.endswith('.xlsx'):
            import_uuid = uuid.uuid4()

            try:
                df = pd.read_excel(plik, sheet_name='Arkusz1', header=0, skiprows=[1], dtype=str)

                # DEBUG: pokaż kolumny
                print("DEBUG - Kolumny w pliku:", df.columns.tolist())

                # Lepsze czyszczenie z mapowaniem dokładnych nazw
                def clean_column_name(col):
                    col_str = str(col).strip().lower()
                    # Dokładne nazwy z pliku
                    if 'szer. geogr., dł. geogr. 1' in col_str or 'szer. geogr., d. geogr. 1' in col_str:
                        return 'wsp1_raw'
                    if 'szer. geogr., dł. geogr. 2' in col_str or 'szer. geogr., d. geogr. 2' in col_str:
                        return 'wsp2_raw'
                    return (col_str.replace(' ', '').replace('.', '').replace(',', '').replace('ä', 'a')
                            .replace('ł', 'l').replace('ć', 'c'))

                df.columns = [clean_column_name(col) for col in df.columns]

                print("DEBUG - Po wyczyszczeniu:", df.columns.tolist())

                obiekty = []
                for idx, row in df.iterrows():
                    # Datetime
                    poczatek = parse_datetime(row.get('poczatek') or row.get('poczatek'))
                    koniec = parse_datetime(row.get('koniec') or row.get('koniec'))

                    # Współrzędne1 - wiele wariantów nazw
                    wsp1_candidates = ['wsp1_raw', 'szergeogrdgeogr1', 'szergeogrdlgeogr1']
                    wsp1_str = next((row.get(cand) for cand in wsp1_candidates if row.get(cand)), '')
                    wsp1 = None
                    if isinstance(wsp1_str, str) and ',' in wsp1_str:
                        parts = wsp1_str.replace('.0000', '').split(',')
                        if len(parts) >= 2:
                            try:
                                lat = float(parts[0].strip())
                                lon = float(parts[1].strip())
                                wsp1 = Point(lon, lat, srid=4326)
                                print(f"DEBUG: Parsed wsp1 {idx}: lat={lat}, lon={lon}")
                            except (ValueError, TypeError) as e:
                                print(f"DEBUG: Błąd parsowania wsp1 {idx}: {e}")

                    # Współrzędne2
                    wsp2_candidates = ['wsp2_raw', 'szergeogrdgeogr2', 'szergeogrdlgeogr2']
                    wsp2_str = next((row.get(cand) for cand in wsp2_candidates if row.get(cand)), '')
                    wsp2 = None
                    if isinstance(wsp2_str, str) and ',' in wsp2_str:
                        parts = wsp2_str.replace('.0000', '').split(',')
                        if len(parts) >= 2:
                            try:
                                lat = float(parts[0].strip())
                                lon = float(parts[1].strip())
                                wsp2 = Point(lon, lat, srid=4326)
                            except (ValueError, TypeError):
                                pass

                    obj = DaneOperator1(
                        import_uuid=import_uuid,
                        poczatek=poczatek,
                        koniec=koniec,
                        czas=parse_numeric(row.get('czas')),
                        msisdn1=row.get('msisdn1'),
                        imei1=row.get('imei1'),
                        kierunek=row.get('kierunek'),
                        msisdn2=row.get('msisdn2'),
                        imei2=row.get('imei2'),
                        typ=row.get('typ'),
                        rodzaj=row.get('rodzaj'),
                        bts1=row.get('bts1'),
                        bts2=row.get('bts2'),
                        lac1=parse_numeric(row.get('lac1')),
                        cid1=parse_numeric(row.get('cid1')),
                        wspolrzedne1=wsp1,
                        azymut1=parse_numeric(row.get('azymut1')),
                        kt1=parse_numeric(row.get('kt1')),
                        zasig1=parse_numeric(row.get('zasig1')),
                        mcc1=parse_numeric(row.get('mcc1')),
                        mnc1=parse_numeric(row.get('mnc1')),
                        lac2=parse_numeric(row.get('lac2')),
                        cid2=parse_numeric(row.get('cid2')),
                        wspolrzedne2=wsp2,
                        azymut2=parse_numeric(row.get('azymut2')),
                        kt2=parse_numeric(row.get('kt2')),
                        zasig2=parse_numeric(row.get('zasig2')),
                        mcc2=parse_numeric(row.get('mcc2')),
                        mnc2=parse_numeric(row.get('mnc2')),
                        imsi1=row.get('imsi1'),
                        imsi2=row.get('imsi2'),
                        przekierowanie=row.get('przekierowanie'),
                        przekier_imei=row.get('przekierimei'),
                        przekier_imsi=row.get('przekierimsi'),
                        przekier_bts=row.get('przekierbts'),
                    )
                    obiekty.append(obj)

                created_count = DaneOperator1.objects.bulk_create(obiekty, ignore_conflicts=True)
                view_url = reverse('operator1_view', kwargs={'uuid': str(import_uuid)})
                messages.success(
                    request,
                    f'Załadowano {len(obiekty)} rekordów (wsp1: {sum(1 for o in obiekty if o.wspolrzedne1)}). '
                    f'<a href="{view_url}" target="_blank">Mapa BTS → UUID: {import_uuid}</a>'
                )
                return redirect('operator1_upload')

            except Exception as e:
                messages.error(request, f'Błąd: {str(e)}')
                print(f"ERROR: {e}")
        else:
            messages.error(request, 'Prześlij .xlsx')

    return render(request, 'core/operator1_upload.html')


def operator1_view(request, uuid):
    dane = DaneOperator1.objects.filter(import_uuid=uuid)
    if not dane.exists():
        raise Http404("Brak danych")

    btsy = []
    for row in dane:
        if row.wspolrzedne1:
            btsy.append({
                'coords': f"{row.wspolrzedne1.y},{row.wspolrzedne1.x}",
                'azymut': float(row.azymut1) if row.azymut1 else 0,
                'kt': float(row.kt1) if row.kt1 else None,  # NULL jeśli brak!
                'zasieg': float(row.zasig1) if row.zasig1 else None,
                'typ': row.typ or '',
                'bts': row.bts1 or '',
            })

    import json
    from django.core.serializers.json import DjangoJSONEncoder

    context = {
        'uuid': str(uuid),
        'dane_count': dane.count(),
        'btsy_count': len(btsy),
        'btsy_json': json.dumps(btsy, cls=DjangoJSONEncoder, ensure_ascii=False),
    }

    return render(request, 'core/operator1_view.html', context)
