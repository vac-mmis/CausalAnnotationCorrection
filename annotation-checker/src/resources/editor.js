"use strict";

const fixMapping = {
    "ReplaceSequence": "Replace with",
    "RemoveSequence": "Remove",
    "WhitelistSignature": "Set new signature",
    "AdaptModel": "Manually add to model",
    "Alert": "Show message",
    "AddToDict": "Add to dictionary",

};

const fixFilter = {
    "Highlight": "info",
    "ReplaceSequence": "change",
    "RemoveSequence": "change",
    "WhitelistSignature": "change",
    "ChangeNumberOfParams": "info",
    "AdaptModel": "info",
    "Alert": "info",
    "AddToDict": "change",

};

function showModal(title, message) {
    let errorModal = new bootstrap.Modal(document.getElementById('myModal'),);
    let header = errorModal._element.getElementsByClassName("modal-title")[0];
    let body = errorModal._element.getElementsByClassName("modal-body")[0];


    header.innerText = title;
    body.innerText = message;

    errorModal.show();

}

class Loading {
    static loaderID() {
        return "loader";
    }

    static labelID() {
        return "lbl-ready";
    }

    static enable(text) {
        let loader = document.getElementById(this.loaderID());
        let label = document.getElementById(this.labelID());

        if (loader.classList.contains("visually-hidden")) {
            label.textContent = text;

            label.classList.remove("text-success");
            label.classList.add("text-danger");


            loader.classList.remove("visually-hidden");
        }
    }

    static info(text) {
        let label = document.getElementById(this.labelID());


        label.classList.remove("text-success", "text-danger");
        label.classList.add("text-warning");
        label.textContent = text;


    }

    static disable() {
        let loader = document.getElementById(this.loaderID());
        let label = document.getElementById(this.labelID());


        if (!loader.classList.contains("visually-hidden")) {
            label.textContent = "ready";

            label.classList.remove("text-danger", "text-warning");
            label.classList.add("text-success");

            loader.classList.add("visually-hidden");
        }
    }
}


function markLines(editor, marker, groupList) {

    if (groupList == null){
        groupList = {};
    }

    let lines = editor.getValue().split("\n");


    let session = editor.getSession();

    for (const key in marker) {
        delete marker[key];
    }

    for (let markerID in session.getMarkers()) {
        session.removeMarker(markerID);
    }


    if ("-1" in groupList) {
        let endRow = session.getDocument().getAllLines().length;
        let endColumn = session.getDocument().getAllLines()[endRow - 1].length;
        let markerID = session.addMarker(new ace.Range(0, 0, endRow, endColumn), "error", "fullLine");
        marker[markerID] = -1 + "," + 0 + "," + 0;
        return;
    }


    for (let i = 0; i < lines.length; i++) {
        if (Object.keys(groupList).includes(String(i + 1))) {
            let format_line = [];

            let line = lines[i];


            let groups = groupList[String(i + 1)];


            let index = 0;
            for (const [key, value] of Object.entries(groups)) {


                let start = key.split(",")[0];
                let end = key.split(",")[1];


                if (line.length === 0) {
                    format_line.push(["wholeline", 0, 1]);
                    index = 0;
                    continue;
                }

                if (start === "-1" && end === "-1") {

                    format_line.push(["wholeline", 0, line.length]);
                    index = line.length;
                    continue;
                }


                if (onlyWarning(value)) {
                    format_line.push(["warning", start, end]);
                } else {
                    format_line.push(["error", start, end]);
                }

                index = end;

            }


            for (let format of format_line) {
                if (format[0] === "error") {

                    let markerID = session.addMarker(new ace.Range(i, format[1], i, format[2]), "error", "text");

                    marker[markerID] = i + 1 + "," + format[1] + "," + format[2];


                } else if (format[0] === "warning") {

                    let markerID = session.addMarker(new ace.Range(i, format[1], i, format[2]), "warning", "text");

                    marker[markerID] = i + 1 + "," + format[1] + "," + format[2];

                } else if (format[0] === "wholeline") {

                    let markerID = session.addMarker(new ace.Range(i, format[1], i, format[2]), "error", "fullLine");


                    marker[markerID] = i + 1 + "," + -1 + "," + -1;

                }

            }

        }


    }


}

function deactivate_lines(lines, lineIndex) {
    if (lineIndex === -1) {
        return;
    }
    for (let i = 0; i < lines.length; i++) {

        if (i <= lineIndex) {

            lines[i].classList.remove("deactivated");
            lines[i].lastChild.setAttribute("contenteditable", "true");
            continue;
        }

        if (lineIndex < lines.length) {

            lines[i].classList.add("deactivated");
            lines[i].lastChild.setAttribute("contenteditable", "false");
        }
    }
}


function colorTabs(annotationData, modelData, modelTabContainer, annotationTabContainer, activeErrorList) {
    let domainErrors = activeErrorList.filter(x => x["error_type"] === "IllegalDomainDescription");
    let problemErrors = activeErrorList.filter(x => x["error_type"] === "IllegalProblemDescription");
    let isWaiting = false;


    formatTab(modelData[0].locked, domainErrors, modelTabContainer.children[0].firstChild.lastChild, true, false);

    if (domainErrors.length > 0) {
        isWaiting = true;
    }
    formatTab(modelData[1].locked, problemErrors, modelTabContainer.children[1].firstChild.lastChild, true, isWaiting);


    for (let i = 0; i < annotationData.length; i++) {

        const normalizePath = (path) => {
            return path.replace(/\\/g, '/');
        };


        let annotationErrors = annotationData[i].errors.filter(x => normalizePath(x["file_name"]) === normalizePath(annotationData[i].file));


        formatTab(annotationData[i].locked, annotationErrors, annotationTabContainer.children[i].firstChild.lastChild, false);

    }


}

function formatTab(locked, errors, tabPill, isModel, isWaiting) {
    if (isWaiting) {
        let cautionIcon = document.createElement("i");
        cautionIcon.classList.add("bi", "bi-hourglass-split", "text-dark", "mx-1");
        tabPill.parentElement.append(cautionIcon);
        tabPill.parentElement.setAttribute("title", "First fix all errors in the domain file to check the problem file");
    } else if (isModel) {
        if (errors.length > 0) {
            let cautionIcon = document.createElement("i");
            cautionIcon.classList.add("bi", "bi-exclamation-circle-fill", "text-danger", "mx-1");

            tabPill.parentElement.append(cautionIcon);

        } else {
            let cautionIcon = document.createElement("i");
            cautionIcon.classList.add("bi", "bi-check-circle-fill", "text-success", "mx-1");

            tabPill.parentElement.append(cautionIcon);
        }
    } else if (errors.filter(x => x["error_level"] === 1).length > 0) {


        tabPill.classList.remove("bg-warning", "bg-success", "bg-danger", "bg-secondary");
        tabPill.classList.add("bg-danger");
        tabPill.textContent += errors.length;


    } else if (errors.filter(x => x["error_level"] === 0).length > 0) {

        tabPill.classList.remove("bg-warning", "bg-success", "bg-danger", "bg-secondary");
        tabPill.classList.add("bg-warning");
        tabPill.textContent += errors.length;


    } else {

        tabPill.classList.remove("bg-warning", "bg-success", "bg-danger", "bg-secondary");
        tabPill.classList.add("bg-success");
        tabPill.textContent += errors.length;
    }

    if (locked) {

        tabPill.parentElement.setAttribute("title", "The file is locked");

        let lockIcon = document.createElement("i");
        lockIcon.classList.add("bi", "bi-lock-fill");
        tabPill.parentElement.append(lockIcon);


    }
}


function onlyWarning(errors) {
    let warnings = true;
    for (let error of errors) {
        if (error["error_level"] !== 0) {
            warnings = false;
            break;
        }
    }
    return warnings;
}

async function saveRequest(viewController) {
    let activeAnnotationID = viewController.control.activeAnnotationIndex;
    let annotationText = viewController.editor.annotation.getValue();
    let activeModelID = viewController.control.activeModelIndex;
    let modelText = viewController.editor.model.getValue();

    let wordList = [...new Set(Array.from(viewController.element.wordList.children).map(element => element.textContent))].sort();


    let line_limit = viewController.active.activeLineIndex;


    viewController.active.annotationCursor = viewController.editor.annotation.getCursorPosition();
    viewController.active.modelCursor = viewController.editor.model.getCursorPosition();

    Loading.enable("saving");

    saveOptionsState(viewController);

    let args = Array.from(document.getElementsByClassName("option-input")).map(x => [x.dataset.option, parseInt(x.dataset.id), (x.classList.contains("form-check-input") ? x.checked : x.value)]);


    let active_statuses = Array.from(document.getElementsByClassName("check-active-checkbox")).map(x => x.checked);


    let response = await fetch("/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json; charset=utf-8"
        },
        body: JSON.stringify({
            "annotationID": activeAnnotationID,
            "annotation": annotationText,
            "modelID": activeModelID,
            "model": modelText,
            "options": args,
            "active_statuses": active_statuses,
            "line_limit": line_limit,
            "word_list": wordList
        })
    }).catch(function () {
        let errorModal = new bootstrap.Modal(document.getElementById('myModal'),);
        errorModal.show();
    });
    Loading.disable();
    viewController.control.unsavedChanges = false;
}

function lockLines(viewController) {

    let session = viewController.editor.annotation.session;

    let line_limit = viewController.active.activeLineIndex;

    if (line_limit === -1) {
        return;
    }


    for (let i = session.getDocument().getAllLines().length - 1; i > line_limit; i--) {

        let range = new ace.Range(i, 0, i, session.getLine(i).length);

        session.addMarker(range, "grayed-out-line", "fullLine");


    }
}

function createTabs(data, navBar, dropdown) {
    navBar.innerText = "";
    dropdown.innerText = "";

    for (let annotation of data) {
        let filename = annotation["file"];
        filename = filename.split("/").pop();

        let item = document.createElement("li");
        item.classList.add("nav-item", "h6");

        item.style.fontSize = "13px";

        let clickableItem = document.createElement("div");
        clickableItem.classList.add("nav-link", "text-dark");

        clickableItem.textContent = filename.split("\\").pop();
        clickableItem.setAttribute("data-id", data.indexOf(annotation));

        clickableItem.style.paddingRight = "5px";
        clickableItem.style.paddingLeft = "10px";

        let badge = document.createElement("span");
        badge.classList.add("badge", "rounded-pill", "bg-primary", "mx-1", "annotation-error-badge");

        badge.textContent = "";
        badge.setAttribute("data-id", data.indexOf(annotation));

        clickableItem.append(badge);

        item.append(clickableItem);
        navBar.append(item);

        dropdown.append(item.cloneNode(true));


    }
}

let stopped = false;
const retry = (fn, interval = 1000) => {
    return new Promise((resolve, reject) => {
        fn()
            .then(resolve => {
                setTimeout(() => {
                    if (stopped === true) {
                        return;
                    }
                    // Passing on "reject" is the important part
                    retry(fn, interval).then(resolve, reject);
                }, interval);
            });
    });
};

function setErrorCountsByCheck(viewController) {
    let errorList = viewController.active.errorList;

    let checks = viewController.data.check;
    let failedCheckID = viewController.active.failedCheckID;
    let errorButtons = viewController.element.errorNumberBadges;
    let activeBoxes = viewController.element.checkActiveCheckboxes;
    let logBadges = viewController.element.logBadges;


    for (let i = 0; i < checks.length; i++) {
        //at first make all gray
        errorButtons[i].classList.remove("btn-danger", "btn-success", "btn-warning", "btn-secondary");
        errorButtons[i].classList.add("btn-secondary");

        errorButtons[i].parentElement.parentElement.classList.remove("bg-gray", "bg-green", "bg-red", "bg-yellow");
        errorButtons[i].parentElement.parentElement.classList.add("bg-gray");


        let amount = errorList.filter(x => x["check_id"] === checks[i]["id"]).length;

        errorButtons[i].textContent = amount;

        if (checks[i].disabled) {


            errorButtons[i].parentElement.parentElement.setAttribute("title", "This check was disabled due to an internal error.");
            errorButtons[i].classList.add("btn-secondary");
            errorButtons[i].style.backgroundColor = "#b4b4b4";
            errorButtons[i].style.border = "none";
            logBadges[i].classList.remove("text-danger", "text-warning");
            logBadges[i].classList.add("text-danger");

            continue;
        }


        if (i > failedCheckID && failedCheckID !== -1 && checks[i].group !== "Async") {
            continue;
        }


        //check if there are only warnings

        let onlyWarnings = (errorList.filter(x => x["check_id"] === checks[i]["id"])).filter(x => x["error_level"] === 1).length === 0;


        if (activeBoxes[i].checked && amount >= 0) {
            errorButtons[i].classList.remove("btn-secondary");
            errorButtons[i].parentElement.parentElement.classList.remove("bg-gray");

            if (amount === 0) {

                errorButtons[i].classList.add("btn-success");
                errorButtons[i].parentElement.parentElement.classList.add("bg-green");

            } else if (onlyWarnings) {
                errorButtons[i].classList.add("btn-warning");
                errorButtons[i].parentElement.parentElement.classList.add("bg-yellow");
            } else {
                errorButtons[i].classList.add("btn-danger");
                errorButtons[i].parentElement.parentElement.classList.add("bg-red");
            }


        }


    }


}


function setActiveOutline(activeAnnotationIndex, navBar) {
    if (navBar.children) {
        for (let listItem of navBar.children) {
            let item = listItem.firstChild;
            item.classList.remove("active");
        }
        Array.from(navBar.children)[activeAnnotationIndex].firstChild.classList.add("active");


    }

}


function showOptions(viewController) {
    let checks = viewController.data.check;
    let optionsContainer = viewController.element.options;

    optionsContainer.innerHTML = "";


    //Continuous checks heading


    let countAsyncChecks = checks.filter(item => item.group === "Async").length;


    for (let check_index = 0; check_index < checks.length; check_index++) {


        let check = checks[check_index];

        if (check_index === 0 && countAsyncChecks > 0) {
            let checkCard = document.createElement("div");
            checkCard.classList.add("card", "card-small", "border-0");
            let asyncTitleBody = document.createElement("div");
            asyncTitleBody.classList.add("card-body", "bg-light-gray");
            let asyncTitle = document.createElement("h6");
            asyncTitle.textContent = "Continuous Checks:";
            asyncTitleBody.append(asyncTitle);
            checkCard.append(asyncTitleBody);
            optionsContainer.append(checkCard);
        }


        if (countAsyncChecks === check_index) {
            let checkCard = document.createElement("div");
            checkCard.classList.add("card", "card-small", "border-0");

            let asyncTitleBody = document.createElement("div");
            asyncTitleBody.classList.add("card-body", "bg-light-gray");

            let asyncTitle = document.createElement("h6");
            asyncTitle.textContent = "Sequential Checks:";
            asyncTitleBody.append(asyncTitle);
            checkCard.append(asyncTitleBody);
            optionsContainer.append(checkCard);

        }


        let disabled = check.disabled;

        let checkCard = document.createElement("div");
        checkCard.classList.add("card");
        checkCard.setAttribute("data-id", check["id"]);

        let cardBody = document.createElement("div");
        cardBody.classList.add("card-body");

        let checkBoxContainer = document.createElement("div");
        checkBoxContainer.classList.add("form-check", "form-switch");
        let checkBox = document.createElement("input");

        checkBox.classList.add("form-check-input", "check-active-checkbox");
        checkBox.type = "checkbox";
        checkBox.id = "active-check-" + check["id"];
        checkBox.name = check["name"];
        checkBox.value = "yes";
        checkBox.checked = check["active"];


        let checkText = document.createElement("label");
        checkText.classList.add("form-check-label", "h6");
        checkText.setAttribute("for", checkBox.id);
        checkText.textContent = check["name"];

        if (disabled) {

            checkBox.setAttribute("disabled", "true");

        }


        let badge = document.createElement("button");
        badge.classList.add("btn", "btn-sm", "btn-secondary", "mx-2", "error-number-badge");
        badge.style.float = "left";
        badge.textContent = "0";
        badge.setAttribute("data-id", check["id"]);


        let detailsButton = document.createElement("button");
        detailsButton.classList.add("btn", "btn-sm", "bi", "bi-gear", "button-detail");
        detailsButton.style.float = "left";

        detailsButton.setAttribute("data-bs-toggle", "collapse");
        detailsButton.setAttribute("data-bs-target", "#collapse-options-" + check["id"]);

        let logButton = document.createElement("button");
        logButton.classList.add("btn", "btn-sm", "bi", "bi-journal-text", "log-badge", "button-info");
        logButton.style.float = "left";

        logButton.setAttribute("data-bs-toggle", "collapse");
        logButton.setAttribute("data-bs-target", "#collapse-logs-" + check["id"]);


        let styleGroup = document.createElement("div");

        styleGroup.style.display = "inline";
        styleGroup.style.float = "right";
        styleGroup.append(detailsButton, logButton);


        checkBoxContainer.append(checkBox, badge, checkText, styleGroup);


        let detailsInfo = document.createElement("div");
        detailsInfo.id = "collapse-options-" + check["id"];
        detailsInfo.classList.add("collapse", "details-info");

        let logsInfo = document.createElement("div");
        logsInfo.setAttribute("spellcheck", "false");
        logsInfo.setAttribute("contenteditable", "true");
        logsInfo.setAttribute("onkeydown", "handleKeyDown(event)");


        logsInfo.id = "collapse-logs-" + check["id"];
        logsInfo.classList.add("collapse", "logs-info");


        let documentation = document.createElement("label");
        documentation.style.fontSize = "12px";
        documentation.innerHTML = check["doc_html"];

        let form = document.createElement("form");


        for (let option in check["options"]) {
            let optionRow = document.createElement("div");
            optionRow.classList.add("form-group", "row", "align-items-center", "my-1");

            let optionColumnLabel = document.createElement("div");
            optionColumnLabel.classList.add("col-3");
            let optionLabel = document.createElement("label");
            optionLabel.classList.add("col-form-label", "col-form-label-sm");
            optionLabel.setAttribute("for", "inputOption" + option);
            optionLabel.textContent = option;
            optionColumnLabel.append(optionLabel);

            let optionColumnInput = document.createElement("div");
            optionColumnInput.classList.add("col-auto");
            if (check["option_types"][option] === "bool") {
                let inputCheckBox = document.createElement("input");
                inputCheckBox.classList.add("form-check-input", "option-input");
                inputCheckBox.setAttribute("data-id", check["id"]);
                inputCheckBox.id = "inputOption" + option;
                inputCheckBox.type = "checkbox";
                inputCheckBox.setAttribute("data-option", option);
                inputCheckBox.checked = check["options"][option];
                optionColumnInput.append(inputCheckBox);
            } else {
                let inputField = document.createElement("input");
                inputField.classList.add("option-input", "form-control", "form-control-sm");
                inputField.setAttribute("data-id", check["id"]);
                inputField.setAttribute("data-option", option);
                inputField.type = "text";
                inputField.value = check["options"][option];
                optionColumnInput.append(inputField);
            }


            optionRow.append(optionColumnLabel, optionColumnInput);
            form.append(optionRow);
        }

        if (Object.entries(check["options"]).length > 0) {
            let saveButton = document.createElement("button");

            saveButton.classList.add("btn", "btn-sm", "btn-success", "my-2", "btn-save-options");
            saveButton.type = "button";
            saveButton.textContent = "Apply";
            form.append(saveButton);
        }


        detailsInfo.append(documentation, form);

        logsInfo.innerHTML = "<br>";

        for (let log of check["logs"]) {
            logsInfo.append(log, document.createElement("br"));

        }


        cardBody.append(checkBoxContainer, detailsInfo, logsInfo);
        checkCard.append(cardBody);

        optionsContainer.append(checkCard);


    }

}

function handleKeyDown(event) {

    let keyCode = event.keyCode || event.which;

    if (event.ctrlKey || event.metaKey && (event.key === 'a' || event.key === 'c')) {

    } else {
        event.preventDefault();
    }
}

function saveOptionsState(viewController) {
    for (let info of viewController.element.detailsInfo) {
        viewController.options.detailsInfo[info.id] = Array.from(info.classList);
    }
    for (let info of viewController.element.logsInfo) {
        viewController.options.logsInfo[info.id] = Array.from(info.classList);
    }


}

function loadOptionsState(viewController) {
    if (Object.keys(viewController.options.detailsInfo).length === 0) {
        saveOptionsState(viewController);
        return;
    }
    if (Object.keys(viewController.options.logsInfo).length === 0) {
        saveOptionsState(viewController);
        return;
    }

    for (let info of viewController.element.detailsInfo) {

        info.classList.remove(...info.classList);
        info.classList.add.apply(info.classList, viewController.options.detailsInfo[info.id]);

    }
    for (let info of viewController.element.logsInfo) {
        info.classList.remove(...info.classList);
        info.classList.add.apply(info.classList, viewController.options.logsInfo[info.id]);
    }
}


function scrollIntoError(editor, errorList, checkID) {
    /** Scroll near first error line to make it easier to find */


    let filteredErrorList = errorList.filter(x => x["check_id"] === checkID);


    if (filteredErrorList.length > 0) {

        let index = (filteredErrorList[0]["line_number"]);
        editor.scrollToLine(index - 1, true, true);


    }
}

async function check() {
    Loading.enable("checking");


    const response = await fetch("check", {
        method: "POST"
    }).catch(function () {
        let errorModal = new bootstrap.Modal(document.getElementById('myModal'),);
        errorModal.show();
    });

    Loading.disable();


}

function collectDeepestElements(object) {
    let elements = [];

    function collect(object) {
        for (let value in object) {
            if (typeof object[value] === 'object') {
                if (Array.isArray(object[value])) {
                    elements.push(...object[value]); // füge Array-Elemente zur Ergebnisliste hinzu
                } else {
                    collect(object[value]); // rekursiver Aufruf für verschachtelte Objekte
                }
            }
        }
    }

    collect(object);
    return elements;
}

function showErrors(errors, outputElement, locked, isModel, errorList) {

    //clear output
    outputElement.innerHTML = "";

    for (let error of errors) {

        let index = errorList.findIndex((e) => {
            return e["advice"] === error["advice"] && e["error_level"] === error["error_level"] &&
                e["error_type"] === error["error_type"] && e["file_name"] === error["file_name"] &&
                e["line_number"] === error["line_number"] && e["incorrect_sequence"][0] === error["incorrect_sequence"][0] &&
                e["incorrect_sequence"][1] === error["incorrect_sequence"][1];
        });

        let tooltip = "";
        if (error["line_number"] === -1) {

            tooltip = error["error_type"];

        } else {
            tooltip = error["error_type"] + " (" + error["incorrect_sequence"][1] + ") in line " + error["line_number"] + ":" + error["incorrect_sequence"][0];
        }

        const dropdown = getFixContainer(tooltip, index, error["fixes"], locked, isModel);

        document.getElementById("output-wrapper").appendChild(dropdown);
    }
}


function getFixContainer(info, errorId, fixes, isLocked, isModel) {


    const container = document.createElement("div");
    container.classList.add("dropdown", "dropend");
    container.style.paddingBottom = "4px";


    const containerInfo = document.createElement("button");
    containerInfo.classList.add("btn", "btn-sm", "btn-outline-dark", "dropdown-toggle", "button-info");
    containerInfo.setAttribute("data-bs-toggle", "dropdown");
    containerInfo.textContent = info;

    const modal = document.createElement("ul");
    modal.classList.add("dropdown-menu");


    for (let i = 0; i < fixes.length; i++) {

        if (isLocked) {
            if (fixFilter[fixes[i][1]] !== "info") {
                continue;
            }
        }
        const modalButton1 = document.createElement("button");
        modalButton1.classList.add("btn", "btn-sm", "btn-outline-dark", "button-fix-error");
        modalButton1.setAttribute("data-error-id", errorId);
        modalButton1.setAttribute("data-error-isModel", isModel);


        let msg = ": " + fixes[i][0];
        let fixID = i;
        if (fixes[i][0] === "{{custom}}") {
            msg = ":";
            fixID = i + ":custom";
        }


        if (fixes[i][0] === null) {
            msg = "";
        }
        if (fixes[i][1] === "AdaptModel") {
            modalButton1.id = "template-toast-body";
            msg = "";
        }

        if (fixes[i][1] === "Alert") {
            modalButton1.id = "template-toast-body";
            msg = "";
        }

        modalButton1.setAttribute("data-fix-id", fixID);
        modalButton1.textContent = fixMapping[fixes[i][1]] + msg;

        const buttonGroup = document.createElement("li");

        buttonGroup.classList.add("dropdown-item", "container");
        buttonGroup.style.width = "400px";
        buttonGroup.appendChild(modalButton1);

        if (fixes[i][0] === "{{custom}}") {
            const custom_input = document.createElement("input");
            custom_input.classList.add("mx-2", "align-middle", "custom-input");
            custom_input.type = "text";
            buttonGroup.appendChild(custom_input);
        }

        if (fixes[i][1] !== "AdaptModel" && fixes[i][1] !== "Alert") {

            const modalButton2 = document.createElement("button");
            modalButton2.classList.add("btn", "btn-sm", "btn-outline-dark", "button-fix-same");
            modalButton2.style.float = "right";
            modalButton2.setAttribute("data-error-id", errorId);
            modalButton2.setAttribute("data-fix-id", fixID);
            modalButton2.textContent = "Fix all";
            buttonGroup.appendChild(modalButton2);
        }


        if (fixMapping[fixes[i][1]] !== null) {
            modal.appendChild(buttonGroup);
        }


    }


    container.append(containerInfo, modal);

    return container;
}