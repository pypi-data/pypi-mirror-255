SELECT t.YEAR, t.MONTH,t.RLEANUPC, t.PRODUCTO, t.PRESENTACION, sum(t.PFSALEQTY) UNIDADES, sum(t.PFSALES) ARS,ROUND(sum(t.PFSALES)/136.531818740357) CHF
FROM 
(SELECT
    YEAR,
    MONTH,
    DAY,
    COUNTRY,
    buying_group_text,
    CLIENTE_ID,
    CLIENTE,
    PRODUCTO,
    INDICACION,
    PRESENTACION,
    DATA_VENDA,
    RLEANUPC,
    RLCOMPCOD_TXTMD,
    DWH_RLCOPA01_ID,
    DWH_RLMATERIA_ID,
    DWH_RLSHIPTO_ID,
    RLACCNTAS_TXTSH,
    RLBILLTYP,
    RLBILLTYP_TXTSH,
    RLCOUNTRY,
    RLPRODHIE_TXTLG,
    RLPRODHIE,
    RLPRODHIE_TXTSH,
    RLPRODHIE_TXTMD,
    RLRECTYPE,
    RLRECTYPE_TXTSH,
    RLDISTRCH,
    RLDISTRCH_TXTSH,
    RLCUSTGRO,
    RLCUSTGRO_TXTSH,
    RLCDLOCBU_TXTSH,
    PFPRODPRE,
    RLMATERIA_TXTMD,
    PFPRODPRE_TXTSH,
    PFPRODFAM,
    PFPRODFAM_TXTSH,
    RLSALESGR,
    RLSALESGR_TXTSH,
    RLBILLNUM,
    RLBILLITE,
    RLSORDIT,
    PFCOGSGSM,
    PFCOGSLVA,
    PFSALEQTY,
    CANTIDAD,
    TERM,
    PFSALES,
    RLGROSSAL,
    RLINVSAL,
    RLTOTCOGS,
    RLCASHDM,
    RLNETSAL,
    NET_VALUE AS NET_VALUE,
    REF_PRICE_VALUE AS REF_PRICE_VALUE,
    ACT_SPECIAL_DISC AS ACT_SPECIAL_DISC,
    INSURANCE_VALUE AS INSURANCE_VALUE,
    FREIGHT_VALUE AS FREIGHT_VALUE,
    --ACT_COM_DISCOUNT
    (
        NET_VALUE - REF_PRICE_VALUE - ACT_SPECIAL_DISC - INSURANCE_VALUE - FREIGHT_VALUE
    ) AS ACT_COM_DISCOUNT,
    rlordreas,
    rlordreas_txtmd
FROM
    (
        SELECT
            rlcustome.rlcustome_txtmd AS cliente,
            rlbuying_group.rlcustome_txtmd AS buying_group_text,
            rlprodhie.rlprodhie_txtmd AS producto,
            rlcopa01.pfdisarea_txtsh AS indicacion,
            rlmateria.rlmateria_txtmd AS presentacion,
            rlsd02.rlinvqtyc AS cantidad,
            rlsd02.rlbuygrp AS buying_group,
            rlcompcod.rlcountry_txtsh AS country,
            rlpmnttrm.rlpmnttrm AS term,
            CASE
                WHEN (rlbilltyp.rlbilltyp = 'ZF9')
                OR (
                    rlbilltyp.rlbilltyp = 'ZAG3'
                    AND rlsd02.rldoctype = 'ZNCF'
                ) THEN 0
                ELSE rlsd02.rlnetvalc
            END AS net_value,
            CASE
                WHEN (rlbilltyp.rlbilltyp = 'ZF9') THEN 0
                ELSE rlsd02.rlsubtot1
            END AS ref_price_value,
            CASE
                WHEN (
                    rlbilltyp.rlbilltyp = 'ZAG3'
                    AND rlsd02.rldoctype = 'ZCR1'
                )
                OR (
                    rlbilltyp.rlbilltyp = 'ZAG5'
                    AND rlsd02.rldoctype = 'ZCA'
                )
                OR (
                    rlbilltyp.rlbilltyp = 'ZAL3'
                    AND (
                        rlsd02.rldoctype = 'ZDR'
                        OR rlsd02.rldoctype = 'ZDR'
                    )
                )
                OR (
                    rlbilltyp.rlbilltyp = 'ZAF2'
                    AND (
                        rlsd02.rldoctype = 'ZDR'
                        OR rlsd02.rldoctype = 'ZCL'
                    )
                )
                OR (
                    rlbilltyp.rlbilltyp = 'ZF2'
                    AND rlsd02.rldoctype = 'ZCL'
                )
                OR (
                    rlbilltyp.rlbilltyp = 'ZAL5'
                    AND rlsd02.rldoctype = 'ZDA'
                )
                OR (rlbilltyp.rlbilltyp = 'ZF9') THEN 0
                ELSE rlsd02.rlsubtot3
            END act_special_disc,
            CASE
                WHEN (rlbilltyp.rlbilltyp = 'ZF9') THEN 0
                ELSE rlsd02.rlcdvzf02
            END insurance_value,
            CASE
                WHEN (
                    rlitcateg.rlitcateg = 'G2TX'
                    AND rlsd02.rldoctype = 'ZCF'
                )
                OR (
                    rlitcateg.rlitcateg = 'ZBWV'
                    AND rlsd02.rldoctype = 'ZDF'
                )
                OR (
                    rlitcateg.rlitcateg = 'G2TX'
                    AND rlsd02.rldoctype = 'ZRT'
                )
                OR (
                    rlitcateg.rlitcateg = 'ZBWV'
                    AND rlsd02.rldoctype = 'ZKB'
                )
                OR (
                    rlitcateg.rlitcateg = 'ZBWV'
                    AND rlsd02.rldoctype = 'ZBRP'
                ) THEN rlsd02.rlsubtot5
                ELSE 0
            END freight_value,
            rlsd02.createdon AS DATA_VENDA,
            nvl(rlmateria.rleanupc, rlmateria.dwh_id) AS rleanupc,
            calendar.calendar_year AS year,
            calendar.calendar_month AS MONTH,
            calendar.calendar_day AS DAY,
            rlcompcod.rlcompcod_txtmd,
            RLCUSTOME.DWH_ID AS cliente_id,
            rlcopa01.dwh_rlcopa01_id,
            rlcopa01.dwh_rlmateria_id,
            rlcopa01.dwh_rlshipto_id,
            rlcopa01.rlaccntas_txtsh,
            rlcopa01.rlbilltyp,
            rlcopa01.rlbilltyp_txtsh,
            rlcopa01.rlcountry,
            rlmateria.rlprodhie_txtlg,
            rlmateria.rlprodhie,
            rlmateria.rlprodhie_txtsh,
            rlmateria.rlprodhie_txtmd,
            rlcopa01.rlrectype,
            rlcopa01.rlrectype_txtsh,
            rlcopa01.rldistrch,
            rlcopa01.rldistrch_txtsh,
            rlcopa01.rlcustgro,
            rlcopa01.rlcustgro_txtsh,
            rlcopa01.rlcdlocbu_txtsh,
            rlcopa01.pfprodpre,
            rlmateria.rlmateria_txtmd,
            rlcopa01.pfprodpre_txtsh,
            rlcopa01.pfprodfam,
            rlcopa01.pfprodfam_txtsh,
            rlcopa01.rlsalesgr,
            rlcopa01.rlsalesgr_txtsh,
            rlcopa01.rlbillnum,
            rlcopa01.rlbillite,
            rlcopa01.rlsordit,
            rlcopa01.pfcogsgsm,
            rlcopa01.pfcogslva,
            rlcopa01.pfsaleqty,
            rlcopa01.pfsales,
            rlcopa01.rlgrossal,
            rlcopa01.rlinvsal,
            rlcopa01.rltotcogs,
            rlcopa01.rlcashdm,
            rlcopa01.pfsales + rlcopa01.rlcashdm AS rlnetsal,
            rlordreas.rlordreas,
            rlordreas.rlordreas_txtmd
        FROM
            scf_latamx_mart.v_ss_f_rlcopa01 rlcopa01
            INNER JOIN scf_latamx_mart.v_ss_f_rlsd02 rlsd02 ON rlsd02.rldocnumb = rlcopa01.rldocnumb
            AND rlsd02.dwh_rlmateria_id = rlcopa01.dwh_rlmateria_id
            AND rlsd02.dwh_rlsalsorg_id = rlcopa01.dwh_rlsalsorg_id
            AND rlsd02.rlsordit = rlcopa01.rlsordit
            AND rlsd02.rlbillnum = rlcopa01.rlbillnum
            AND rlsd02.rlbillite = rlcopa01.rlbillite
            INNER JOIN scf_latamx_mart.v_ss_d_rlbilltyp rlbilltyp ON rlsd02.dwh_rlbilltyp_id = rlbilltyp.dwh_id
            INNER JOIN scf_latamx_mart.v_ss_d_rlmateria rlmateria ON rlcopa01.dwh_rlmateria_id = rlmateria.dwh_id
            INNER JOIN scf_latamx_mart.v_ss_d_rlcustome rlcustome ON rlcopa01.dwh_rlpayer_id = rlcustome.dwh_id
            INNER JOIN scf_latamx_mart.v_ss_d_rlcustome rlbuying_group ON rlsd02.rlbuygrp = rlbuying_group.dwh_source_key_rlcustome
            INNER JOIN scf_latamx_mart.v_ss_d_rlcompcod rlcompcod ON rlcopa01.dwh_rlcompcod_id = rlcompcod.dwh_id
            INNER JOIN scf_latamx_mart.v_ss_d_rlitcateg rlitcateg ON rlitcateg.dwh_id = rlsd02.dwh_rlitcateg_id
            INNER JOIN scf_latamx_mart.v_ss_d_rlpmnttrm rlpmnttrm ON rlpmnttrm.dwh_id = rlsd02.dwh_rlpmnttrm_id
            LEFT JOIN scf_latamx_mart.v_ss_d_calendar calendar ON calendar.dwh_id = rlcopa01.dwh_calday_id
            LEFT JOIN scf_latamx_mart.v_ss_d_rlprodhie rlprodhie ON rlprodhie.dwh_id = rlsd02.dwh_rlprodhie_id
            LEFT JOIN scf_latamx_mart.V_SS_D_RLORDREAS rlordreas ON rlsd02.dwh_rlordreas_id = rlordreas.dwh_id
        WHERE
            rlcompcod.rlcompcod IN ('2640')
            AND calendar.period_start_date >= TRUNC(ADD_MONTHS(SYSDATE, -48), 'SYYYY')
            AND rlcopa01.currency IN ('ARS')
            AND rlcopa01.rlcurtype = '10'
            AND rlcopa01.rldistrch IN ('30', '31')
    )) t
WHERE
YEAR=2024
GROUP BY t.YEAR, t.MONTH,t.RLEANUPC, t.PRODUCTO, t.PRESENTACION
ORDER BY t.YEAR, t.MONTH,t.PRODUCTO, t.PRESENTACION
