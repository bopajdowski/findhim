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
    """Bezpieczne parsowanie datetime + timezone-aware (USE_TZ=True)."""
    if pd_types.is_scalar(val) and pd.notna(val) and str(val).strip():
        dt = pd.to_datetime(val, errors="coerce")
        if pd.notna(dt):
            # dt z pandas jest "naive", więc robimy aware w TIME_ZONE z settings
            return timezone.make_aware(dt)
    return None


def parse_numeric(val):
    """Bezpieczne parsowanie liczby; zwraca float/int lub None."""
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
                skiprows=[1],  # wiersz 2 pusty
                dtype=str,
            )

            def clean_column_name(col):
                col_str = str(col).strip().lower()

                # Dokładne nazwy z pliku
                if "szer. geogr., dł. geogr. 1" in col_str or "szer. geogr., d. geogr. 1" in col_str:
                    return "wsp1_raw"
                if "szer. geogr., dł. geogr. 2" in col_str or "szer. geogr., d. geogr. 2" in col_str:
                    return "wsp2_raw"

                # standar
