import{v as i}from"./index.3.5.1a515780.js";import"vue";import"vue-content-loader";import"./_commonjsHelpers.3.5.1a515780.js";function s(t){return t%100==2}function u(t){return t%100==3||t%100==4}function n(t,e,a,r){var m=t+" ";switch(a){case"s":return e||r?"nekaj sekund":"nekaj sekundami";case"m":return e?"ena minuta":"eno minuto";case"mm":return s(t)?m+(e||r?"minuti":"minutama"):u(t)?m+(e||r?"minute":"minutami"):m+(e||r?"minut":"minutami");case"h":return e?"ena ura":"eno uro";case"hh":return s(t)?m+(e||r?"uri":"urama"):u(t)?m+(e||r?"ure":"urami"):m+(e||r?"ur":"urami");case"d":return e||r?"en dan":"enim dnem";case"dd":return s(t)?m+(e||r?"dneva":"dnevoma"):m+(e||r?"dni":"dnevi");case"M":return e||r?"en mesec":"enim mesecem";case"MM":return s(t)?m+(e||r?"meseca":"mesecema"):u(t)?m+(e||r?"mesece":"meseci"):m+(e||r?"mesecev":"meseci");case"y":return e||r?"eno leto":"enim letom";case"yy":return s(t)?m+(e||r?"leti":"letoma"):u(t)?m+(e||r?"leta":"leti"):m+(e||r?"let":"leti")}}var _={name:"sl",weekdays:"nedelja_ponedeljek_torek_sreda_četrtek_petek_sobota".split("_"),months:"januar_februar_marec_april_maj_junij_julij_avgust_september_oktober_november_december".split("_"),weekStart:1,weekdaysShort:"ned._pon._tor._sre._čet._pet._sob.".split("_"),monthsShort:"jan._feb._mar._apr._maj._jun._jul._avg._sep._okt._nov._dec.".split("_"),weekdaysMin:"ne_po_to_sr_če_pe_so".split("_"),ordinal:function(t){return t+"."},formats:{LT:"H:mm",LTS:"H:mm:ss",L:"DD.MM.YYYY",LL:"D. MMMM YYYY",LLL:"D. MMMM YYYY H:mm",LLLL:"dddd, D. MMMM YYYY H:mm",l:"D. M. YYYY"},relativeTime:{future:"čez %s",past:"pred %s",s:n,m:n,mm:n,h:n,hh:n,d:n,dd:n,M:n,MM:n,y:n,yy:n}};i.locale(_,null,!0);export{_ as default};
