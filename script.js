function toggle_personal() {
    document.getElementById('personal').classList.toggle('no_display');
    if(document.getElementById('unfold_personal').innerHTML == "ausklappen") {
        document.getElementById('unfold_personal').innerHTML = "einklappen";
    } else {
        document.getElementById('unfold_personal').innerHTML = "ausklappen";
    }
}

function toggle_timePerDay() {
    document.getElementById('timePerDay').classList.toggle('no_display');
    if(document.getElementById('unfold_timePerDay').innerHTML == "ausklappen") {
        document.getElementById('unfold_timePerDay').innerHTML = "einklappen";
    } else {
        document.getElementById('unfold_timePerDay').innerHTML = "ausklappen";
    }
}

function onChange_file(event) {
    let reader = new FileReader();
    reader.onload = onReaderLoad;
    reader.readAsText(event.target.files[0]);
}

function onReaderLoad(event){
    console.log(event.target.result);
    let obj = JSON.parse(event.target.result);
    fillData(obj);
}

function fillData(obj){
    for(const key in obj) {
        document.getElementById(key).value = obj[key];
    }
}

function download_personal() {
    let obj = {};
    const keys = ["nachname", "vornamen", "geburtsdatum", "personalnummer", "kostenstelle", "vorgesetzte:r", "struktureinheit", "startmonat", "startjahr", "endmonat", "endjahr", "wochenstunden"];
    for(let i = 0; i < keys.length; i++) {
        obj[keys[i]] = document.getElementById(keys[i]).value;
    }
    let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
    let dlAnchorElem = document.getElementById("downloadAnchorElem");
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "personal_info.json");
    dlAnchorElem.click();
}

function download_timePerDay() {
    let obj = {};
    for(let i = 0; i < 5; i++) {
        obj["startzeit_"+i] = document.getElementById("startzeit_"+i).value;
    }
    for(let i = 0; i < 5; i++) {
        obj["arbeitszeit_"+i] = document.getElementById("arbeitszeit_"+i).value;
    }
    let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
    let dlAnchorElem = document.getElementById("downloadAnchorElem");
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "timePerDay_info.json");
    dlAnchorElem.click();
}

function autofill_timePerDay() {
    let weeklyHours = document.getElementById("wochenstunden").value;
    weeklyHours = weeklyHours == "" ? "0" : weeklyHours.replaceAll(",", ".");
    let dailyHours = parseFloat(weeklyHours) / 5;
    for(let i = 0; i < 5; i++) {
        document.getElementById("arbeitszeit_" + i).value = dailyHours;
    }
}

window.onload = function() {
    document.getElementById('personal_info').addEventListener('change', onChange_file);
    document.getElementById('timePerDay_info').addEventListener('change', onChange_file);
};