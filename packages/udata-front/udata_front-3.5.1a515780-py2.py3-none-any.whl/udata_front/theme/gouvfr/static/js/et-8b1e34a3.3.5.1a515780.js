import{v as m}from"./index.3.5.1a515780.js";import"vue";import"vue-content-loader";import"./_commonjsHelpers.3.5.1a515780.js";function a(_,s,e,u){var t={s:["mõne sekundi","mõni sekund","paar sekundit"],m:["ühe minuti","üks minut"],mm:["%d minuti","%d minutit"],h:["ühe tunni","tund aega","üks tund"],hh:["%d tunni","%d tundi"],d:["ühe päeva","üks päev"],M:["kuu aja","kuu aega","üks kuu"],MM:["%d kuu","%d kuud"],y:["ühe aasta","aasta","üks aasta"],yy:["%d aasta","%d aastat"]};return s?(t[e][2]?t[e][2]:t[e][1]).replace("%d",_):(u?t[e][0]:t[e][1]).replace("%d",_)}var i={name:"et",weekdays:"pühapäev_esmaspäev_teisipäev_kolmapäev_neljapäev_reede_laupäev".split("_"),weekdaysShort:"P_E_T_K_N_R_L".split("_"),weekdaysMin:"P_E_T_K_N_R_L".split("_"),months:"jaanuar_veebruar_märts_aprill_mai_juuni_juuli_august_september_oktoober_november_detsember".split("_"),monthsShort:"jaan_veebr_märts_apr_mai_juuni_juuli_aug_sept_okt_nov_dets".split("_"),ordinal:function(_){return _+"."},weekStart:1,relativeTime:{future:"%s pärast",past:"%s tagasi",s:a,m:a,mm:a,h:a,hh:a,d:a,dd:"%d päeva",M:a,MM:a,y:a,yy:a},formats:{LT:"H:mm",LTS:"H:mm:ss",L:"DD.MM.YYYY",LL:"D. MMMM YYYY",LLL:"D. MMMM YYYY H:mm",LLLL:"dddd, D. MMMM YYYY H:mm"}};m.locale(i,null,!0);export{i as default};
