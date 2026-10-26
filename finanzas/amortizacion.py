"""Motor de amortización con la metodología exacta de clase (UPB):
- Cuota fija (Francés).
- Abono a capital constante (Alemán).
- Periodos de gracia con pago de intereses (gracia parcial) y sin pago de intereses (gracia total/capitalización).
- Pagos extras programados periódicos (descuento por VA en cuota fija, descuento nominal en abono constante).
- Abonos extraordinarios puntuales (reducción de plazo o reducción de cuota).
- Columna de comprobación de Valor Presente cuota a cuota (Vr. cuotas mes 0).
"""

from finanzas import tasas
from finanzas.series import factor_vp

SISTEMAS = {
    "frances": "Cuota fija",
    "aleman": "Abono constante a capital",
}

MODALIDADES_GRACIA = {
    "ninguno": "Sin periodo de gracia",
    "con_interes": "Con periodo de gracia y pago de intereses (Parcial)",
    "sin_interes": "Con periodo de gracia y sin pago de intereses (Total / Capitalización)",
}

TIPOS_PAGO_EXTRA = {
    "ninguno": "Sin pagos extras",
    "periodico": "Pagos extras periódicos pactados (ej. semestrales)",
    "puntual": "Abono extraordinario puntual en un periodo específico",
}

EFECTOS_PUNTUAL = {
    "reducir_plazo": "Reducir plazo (mantener cuota)",
    "reducir_cuota": "Reducir cuota (mantener plazo)",
}


def cuota_fija(saldo, i, n):
    """Cuota uniforme para amortizar un saldo en n periodos a la tasa periódica i."""
    if n <= 0:
        return 0.0
    if i == 0:
        return saldo / n
    return saldo / factor_vp(i, n)


def tabla_amortizacion(
    monto,
    i_periodica,
    n,
    sistema="frances",
    modalidad_gracia="ninguno",
    periodos_gracia=0,
    tipo_pago_extra="ninguno",
    # Parámetros para pagos extras periódicos (metodología UPB de clase):
    frecuencia_extra_meses=6,
    monto_extra_periodico=0.0,
    tasa_ea=None,
    # Parámetros para abono extraordinario puntual:
    abono_puntual_periodo=0,
    abono_puntual_monto=0.0,
    efecto_puntual="reducir_plazo",
):
    """Construye la tabla de amortización con la metodología de clase UPB.

    Retorna una lista de diccionarios con:
    - periodo
    - saldo_inicial
    - intereses
    - abono_capital (ordinario)
    - cuota_extra
    - total_abono (abono_capital + cuota_extra)
    - cuota (cuota ordinaria a pagar)
    - pago_total (cuota ordinaria + cuota_extra)
    - saldo_final
    - vr_cuota_mes_0 (valor de la cuota descontada a t=0)
    """
    if monto <= 0:
        raise ValueError("El capital debe ser mayor a cero.")
    if n <= 0:
        raise ValueError("El total de periodos debe ser mayor a cero.")
    if periodos_gracia >= n:
        raise ValueError("El periodo de gracia debe ser menor al plazo total.")

    filas = [
        {
            "periodo": 0,
            "saldo_inicial": float(monto),
            "intereses": 0.0,
            "abono_capital": 0.0,
            "cuota_extra": 0.0,
            "total_abono": 0.0,
            "cuota": 0.0,
            "pago_total": 0.0,
            "saldo_final": float(monto),
            "vr_cuota_mes_0": 0.0,
        }
    ]

    saldo_actual = float(monto)
    n_amortizacion = n - periodos_gracia
    tiene_extras_periodicos = (
        tipo_pago_extra == "periodico"
        and monto_extra_periodico > 0
        and frecuencia_extra_meses > 0
    )

    # 1. Ajuste previo para pagos extras periódicos pactados (ejercicios de clase)
    if tiene_extras_periodicos and periodos_gracia == 0:
        total_cuotas_extras = n // frecuencia_extra_meses
        if sistema == "frances":
            # Metodología de clase UPB:
            # Se calcula la tasa equivalente para la frecuencia del pago extra (ej. semestral a partir de la EA)
            if tasa_ea is None:
                tasa_ea = (1 + i_periodica) ** 12 - 1
            periodos_ano_extra = 12 / frecuencia_extra_meses
            i_extra = (1 + tasa_ea) ** (1 / periodos_ano_extra) - 1

            # Valor actual de las cuotas extras
            va_cuotas_extras = monto_extra_periodico * factor_vp(i_extra, total_cuotas_extras)
            # Valor actual a amortizar con las cuotas ordinarias
            va_cuotas_ordinarias = monto - va_cuotas_extras
            cuota_ordinaria_base = cuota_fija(va_cuotas_ordinarias, i_periodica, n)
            abono_capital_fijo = 0.0
        else:  # aleman
            # Metodología de clase UPB:
            # Se descuenta la suma nominal de los abonos extras:
            total_abonos_extras_nominal = total_cuotas_extras * monto_extra_periodico
            capital_ordinario = monto - total_abonos_extras_nominal
            abono_capital_fijo = capital_ordinario / n
            cuota_ordinaria_base = 0.0
    else:
        # Sin pagos extras periódicos
        if sistema == "frances":
            cuota_ordinaria_base = cuota_fija(saldo_actual, i_periodica, n_amortizacion)
            abono_capital_fijo = 0.0
        else:
            cuota_ordinaria_base = 0.0
            abono_capital_fijo = saldo_actual / n_amortizacion if n_amortizacion > 0 else 0.0

    t = 1
    while saldo_actual > 1e-4 and t <= n * 2:
        saldo_inicio = saldo_actual
        intereses_t = saldo_inicio * i_periodica

        # --- A. Periodo de gracia ---
        if t <= periodos_gracia and modalidad_gracia != "ninguno":
            if modalidad_gracia == "sin_interes":
                # Gracia total / periodo muerto: intereses se capitalizan, cuota = 0
                intereses_cobrados = intereses_t
                cuota_t = 0.0
                abono_capital_t = 0.0
                cuota_extra_t = 0.0
                pago_total_t = 0.0
                saldo_actual = saldo_inicio + intereses_t
            else:
                # Gracia con pago de intereses (parcial): se pagan intereses, capital no cambia
                intereses_cobrados = intereses_t
                cuota_t = intereses_t
                abono_capital_t = 0.0
                cuota_extra_t = 0.0
                pago_total_t = intereses_t
                saldo_actual = saldo_inicio

            vr_mes_0 = pago_total_t / ((1 + i_periodica) ** t) if i_periodica > 0 else pago_total_t

            filas.append({
                "periodo": t,
                "saldo_inicial": saldo_inicio,
                "intereses": intereses_cobrados,
                "abono_capital": abono_capital_t,
                "cuota_extra": cuota_extra_t,
                "total_abono": abono_capital_t + cuota_extra_t,
                "cuota": cuota_t,
                "pago_total": pago_total_t,
                "saldo_final": max(0.0, saldo_actual),
                "vr_cuota_mes_0": vr_mes_0,
            })

            # Al terminar el periodo de gracia, se recalcula la cuota para los periodos restantes
            if t == periodos_gracia:
                periodos_restantes = n - periodos_gracia
                if sistema == "frances":
                    cuota_ordinaria_base = cuota_fija(saldo_actual, i_periodica, periodos_restantes)
                else:
                    abono_capital_fijo = saldo_actual / periodos_restantes

            t += 1
            continue

        # --- B. Periodo de amortización regular ---
        cuota_extra_t = 0.0

        # 1. Pago extra periódico programado (cada k meses)
        if tiene_extras_periodicos and (t % frecuencia_extra_meses == 0):
            cuota_extra_t += monto_extra_periodico

        # 2. Abono extraordinario puntual
        if (
            tipo_pago_extra == "puntual"
            and t == abono_puntual_periodo
            and abono_puntual_monto > 0
        ):
            cuota_extra_t += abono_puntual_monto

        if sistema == "frances":
            cuota_t = cuota_ordinaria_base
            abono_capital_t = cuota_t - intereses_t
        else:  # aleman
            abono_capital_t = abono_capital_fijo
            cuota_t = abono_capital_t + intereses_t

        # Ajuste de cierre si el abono ordinario supera el saldo
        if abono_capital_t > saldo_inicio:
            abono_capital_t = saldo_inicio
            cuota_t = abono_capital_t + intereses_t

        # Ajuste de abono extra si supera el saldo restante
        saldo_remanente = saldo_inicio - abono_capital_t
        if cuota_extra_t > saldo_remanente:
            cuota_extra_t = max(0.0, saldo_remanente)

        total_abono_t = abono_capital_t + cuota_extra_t
        saldo_actual = saldo_inicio - total_abono_t
        pago_total_t = cuota_t + cuota_extra_t

        vr_mes_0 = pago_total_t / ((1 + i_periodica) ** t) if i_periodica > 0 else pago_total_t

        filas.append({
            "periodo": t,
            "saldo_inicial": saldo_inicio,
            "intereses": intereses_t,
            "abono_capital": abono_capital_t,
            "cuota_extra": cuota_extra_t,
            "total_abono": total_abono_t,
            "cuota": cuota_t,
            "pago_total": pago_total_t,
            "saldo_final": max(0.0, saldo_actual),
            "vr_cuota_mes_0": vr_mes_0,
        })

        # Si hubo abono puntual y el efecto es reducir cuota, se recalcula la cuota restante
        if (
            tipo_pago_extra == "puntual"
            and cuota_extra_t > 0
            and efecto_puntual == "reducir_cuota"
            and saldo_actual > 1e-4
        ):
            periodos_restantes = n - t
            if periodos_restantes > 0:
                if sistema == "frances":
                    cuota_ordinaria_base = cuota_fija(saldo_actual, i_periodica, periodos_restantes)
                else:
                    abono_capital_fijo = saldo_actual / periodos_restantes

        t += 1

    return filas


def resumen_amortizacion(filas):
    """Calcula métricas clave a partir de la tabla de amortización."""
    if not filas or len(filas) <= 1:
        return {
            "monto": 0.0,
            "total_intereses": 0.0,
            "total_abono_capital": 0.0,
            "total_cuotas_extras": 0.0,
            "total_pagado": 0.0,
            "plazo_efectivo": 0,
            "cuota_inicial": 0.0,
            "cuota_final": 0.0,
            "suma_vr_cuotas_mes_0": 0.0,
        }

    monto = filas[0]["saldo_inicial"]
    cuotas_ordinarias = [f["cuota"] for f in filas[1:] if f["cuota"] > 0]
    total_intereses = sum(f["intereses"] for f in filas[1:])
    total_abono_capital = sum(f["abono_capital"] for f in filas[1:])
    total_cuotas_extras = sum(f["cuota_extra"] for f in filas[1:])
    total_pagado = sum(f["pago_total"] for f in filas[1:])
    plazo_efectivo = len(filas) - 1
    cuota_inicial = cuotas_ordinarias[0] if cuotas_ordinarias else 0.0
    cuota_final = cuotas_ordinarias[-1] if cuotas_ordinarias else 0.0
    suma_vr_cuotas_mes_0 = sum(f["vr_cuota_mes_0"] for f in filas[1:])

    return {
        "monto": monto,
        "total_intereses": total_intereses,
        "total_abono_capital": total_abono_capital,
        "total_cuotas_extras": total_cuotas_extras,
        "total_pagado": total_pagado,
        "plazo_efectivo": plazo_efectivo,
        "cuota_inicial": cuota_inicial,
        "cuota_final": cuota_final,
        "suma_vr_cuotas_mes_0": suma_vr_cuotas_mes_0,
    }


def comparar_sistemas(monto, i, n):
    """Compara cuota fija y abono constante a capital para los mismos parámetros base."""
    tf = tabla_amortizacion(monto, i, n, sistema="frances")
    ta = tabla_amortizacion(monto, i, n, sistema="aleman")
    rf = resumen_amortizacion(tf)
    ra = resumen_amortizacion(ta)

    return {
        "frances": rf,
        "aleman": ra,
        "diferencia_intereses": rf["total_intereses"] - ra["total_intereses"],
    }
