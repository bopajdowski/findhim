import json
import uuid

import pandas as pd
import pandas.api.types as pd_types

from django.contrib import messages
from django.contrib.gis.geos import Point
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from .models import DaneOperator1


def parse_datetime(val):
    if pd_types.is_scalar(val) and pd.notna(val) and str(val).strip():
        dt = pd.to_datetime(val, errors="coerce")
        if pd.notna(dt):
            return timezone.make_aware(dt)
    return None


def parse_numeric(val):
    if pd.notna(val) and str(val).strip() != "":
        num = pd.to_numeric(val, errors="coerce")
        if pd.notna(num):
            return float(num)
    return None


def operator1_upload(request):
    if request.method == "POST":
        plik = request.FILES.get("plik")

        if not plik or not plik.name.endswith(".xlsx"):
            messages.error(request, "Prześlij prawidłowy plik .xlsx")
            return redirect("operator1_upload")

        import_uuid = uuid.uuid4()

        try:
            df = pd.read_excel(
                plik,
                sheet_name="Arkusz1",
                header=0,
                skiprows=[1],
                dtype=str,
            )

            def clean_column_name(col):
                raw = str(col).strip()

                # 1) Mapowanie 1:1 (nagłówek XLSX -> pole w modelu)
                direct = {
                    "Początek": "poczatek",
                    "Koniec": "koniec",
                    "Czas": "czas",

                    "Szer. geogr., dł. geogr. 1": "wsp1_raw",
                    "Szer. geogr., dł. geogr. 2": "wsp2_raw",

                    "Azymut 1": "azymut1",
                    "Kąt 1": "kt1",
                    "Zasięg 1": "zasig1",

                    "Azymut 2": "azymut2",
                    "Kąt 2": "kt2",
                    "Zasięg 2": "zasig2",

                    "BTS 1": "bts1",
                    "BTS 2": "bts2",
                    "LAC 1": "lac1",
                    "CID 1": "cid1",
                    "LAC 2": "lac2",
                    "CID 2": "cid2",
                    "MCC 1": "mcc1",
                    "MNC 1": "mnc1",
                    "MCC 2": "mcc2",
                    "MNC 2": "mnc2",
                    "MSISDN 1": "msisdn1",
                    "IMEI 1": "imei1",
                    "MSISDN 2": "msisdn2",
                    "IMEI 2": "imei2",
                    "Typ": "typ",
                    "Rodzaj": "rodzaj",
                    "Kierunek": "kierunek",
                    "IMSI 1": "imsi1",
                    "IMSI 2": "imsi2",
                    "Przekierowanie": "przekierowanie",
                    "Przekier. IMEI": "przekierimei",
                    "Przekier. IMSI": "przekierimsi",
                    "Przekier. BTS": "przekierbts",
                }
                if raw in direct:
                    return direct[raw]

                # 2) Fallback – jakby były minimalnie inne spacje/kropki (bezpieczny)
                s = raw.lower()
                s = (
                    s.replace(" ", "")
                    .replace(".", "")
                    .replace(",", "")
                    .replace("ł", "l")
                    .replace("ć", "c")
                    .replace("ń", "n")
                    .replace("ó", "o")
                    .replace("ś", "s")
                    .replace("ż", "z")
                    .replace("ź", "z")
                )
                return s

            df.columns = [clean_column_name(c) for c in df.columns]

            obiekty = []
            for _, row in df.iterrows():
                poczatek = parse_datetime(row.get("poczatek"))
                koniec = parse_datetime(row.get("koniec"))

                wsp1 = None
                wsp1_str = row.get("wsp1_raw") or ""
                if isinstance(wsp1_str, str) and "," in wsp1_str:
                    parts = wsp1_str.replace(".0000", "").split(",")
                    if len(parts) >= 2:
                        try:
                            lat = float(parts[0].strip())
                            lon = float(parts[1].strip())
                            wsp1 = Point(lon, lat, srid=4326)
                        except (ValueError, TypeError):
                            wsp1 = None

                wsp2 = None
                wsp2_str = row.get("wsp2_raw") or ""
                if isinstance(wsp2_str, str) and "," in wsp2_str:
                    parts = wsp2_str.replace(".0000", "").split(",")
                    if len(parts) >= 2:
                        try:
                            lat = float(parts[0].strip())
                            lon = float(parts[1].strip())
                            wsp2 = Point(lon, lat, srid=4326)
                        except (ValueError, TypeError):
                            wsp2 = None

                obiekty.append(
                    DaneOperator1(
                        import_uuid=import_uuid,
                        poczatek=poczatek,
                        koniec=koniec,
                        czas=parse_numeric(row.get("czas")),
                        msisdn1=row.get("msisdn1"),
                        imei1=row.get("imei1"),
                        kierunek=row.get("kierunek"),
                        msisdn2=row.get("msisdn2"),
                        imei2=row.get("imei2"),
                        typ=row.get("typ"),
                        rodzaj=row.get("rodzaj"),
                        bts1=row.get("bts1"),
                        bts2=row.get("bts2"),
                        lac1=parse_numeric(row.get("lac1")),
                        cid1=parse_numeric(row.get("cid1")),
                        wspolrzedne1=wsp1,
                        azymut1=parse_numeric(row.get("azymut1")),
                        kt1=parse_numeric(row.get("kt1")),
                        zasig1=parse_numeric(row.get("zasig1")),
                        mcc1=parse_numeric(row.get("mcc1")),
                        mnc1=parse_numeric(row.get("mnc1")),
                        lac2=parse_numeric(row.get("lac2")),
                        cid2=parse_numeric(row.get("cid2")),
                        wspolrzedne2=wsp2,
                        azymut2=parse_numeric(row.get("azymut2")),
                        kt2=parse_numeric(row.get("kt2")),
                        zasig2=parse_numeric(row.get("zasig2")),
                        mcc2=parse_numeric(row.get("mcc2")),
                        mnc2=parse_numeric(row.get("mnc2")),
                        imsi1=row.get("imsi1"),
                        imsi2=row.get("imsi2"),
                        przekierowanie=row.get("przekierowanie"),
                        przekier_imei=row.get("przekierimei"),
                        przekier_imsi=row.get("przekierimsi"),
                        przekier_bts=row.get("przekierbts"),
                    )
                )

            DaneOperator1.objects.bulk_create(obiekty, ignore_conflicts=True)

            view_url = reverse("operator1_view", kwargs={"uuid": str(import_uuid)})
            messages.success(
                request,
                (
                    f'Załadowano {len(obiekty)} rekordów (geo: {sum(1 for o in obiekty if o.wspolrzedne1)}). '
                    f'<a href="{view_url}" target="_blank">Mapa BTS → UUID: {import_uuid}</a>'
                ),
            )
            return redirect("operator1_upload")

        except Exception as e:
            messages.error(request, f"Błąd: {str(e)}")
            return redirect("operator1_upload")

    return render(request, "core/operator1_upload.html")


from django.db.models import Min, Max

def operator1_view(request, uuid):
    qs = DaneOperator1.objects.filter(import_uuid=uuid)
    if not qs.exists():
        raise Http404("Brak danych dla UUID")

    # zakres czasu na podstawie poczatek/koniec
    agg = qs.aggregate(min_p=Min("poczatek"), max_k=Max("koniec"), max_p=Max("poczatek"))
    min_dt = agg["min_p"]
    max_dt = agg["max_k"] or agg["max_p"]

    # bierzemy rekordy z geo + azymut/kt/zasieg (jak wcześniej) + czas
    qs_ok = qs.filter(
        wspolrzedne1__isnull=False,
        azymut1__isnull=False,
        kt1__isnull=False,
        zasig1__isnull=False,
        poczatek__isnull=False,
    )

    # events = rekordy czasowe, z których potem robi się lista BTSów
    events = []
    for row in qs_ok.only("poczatek", "koniec", "wspolrzedne1", "azymut1", "kt1", "zasig1", "typ", "bts1"):
        p = row.wspolrzedne1
        events.append({
            "start_ms": int(row.poczatek.timestamp() * 1000) if row.poczatek else None,
            "end_ms": int(row.koniec.timestamp() * 1000) if row.koniec else None,
            "coords": f"{p.y},{p.x}",
            "azymut": float(row.azymut1),
            "kt": float(row.kt1),
            "zasieg": float(row.zasig1),
            "typ": row.typ or "",
            "bts": row.bts1 or "",
        })

    context = {
        "uuid": str(uuid),
        "dane_count": qs.count(),
        "min_ts": int(min_dt.timestamp() * 1000) if min_dt else None,
        "max_ts": int(max_dt.timestamp() * 1000) if max_dt else None,
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
    }
    return render(request, "core/operator1_view.html", context)


def operator1_heatmap1(request, uuid):
    qs = DaneOperator1.objects.filter(import_uuid=uuid)
    if not qs.exists():
        raise Http404("Brak danych dla UUID")

    agg = qs.aggregate(min_p=Min("poczatek"), max_k=Max("koniec"), max_p=Max("poczatek"))
    min_dt = agg["min_p"]
    max_dt = agg["max_k"] or agg["max_p"]

    qs_ok = qs.filter(
        wspolrzedne1__isnull=False,
        azymut1__isnull=False,
        kt1__isnull=False,
        zasig1__isnull=False,
        poczatek__isnull=False,
    )

    events = []
    for row in qs_ok.only("poczatek", "koniec", "wspolrzedne1", "azymut1", "kt1", "zasig1", "typ", "bts1"):
        p = row.wspolrzedne1
        events.append({
            "start_ms": int(row.poczatek.timestamp() * 1000) if row.poczatek else None,
            "end_ms": int(row.koniec.timestamp() * 1000) if row.koniec else None,
            "coords": f"{p.y},{p.x}",  # lat,lon
            "azymut": float(row.azymut1),
            "kt": float(row.kt1),
            "zasieg": float(row.zasig1),
            "typ": row.typ or "",
            "bts": row.bts1 or "",
        })

    context = {
        "uuid": str(uuid),
        "dane_count": qs.count(),
        "min_ts": int(min_dt.timestamp() * 1000) if min_dt else None,
        "max_ts": int(max_dt.timestamp() * 1000) if max_dt else None,
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
    }
    return render(request, "core/operator1_heatmap.html", context)