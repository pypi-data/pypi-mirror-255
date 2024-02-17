let devices = function() {
    "use strict";

    let config = {
        deviceList: "#ys-devices-list",
        deviceDialog: "#ys-device-dialog",
        progressBar: "#ys-progress",
        progress: 'div#ys-progress'
    };

    let c = config;

    /**
     * Retrieve the list of existing device profiles from the server.
     */
    function listDevices() {
        return $.ajax({
            url: "/devices/list/",
            type: "GET",
            datatype: 'json',
        });
    }

    /**
     * Get the contents of a single device profile from the server.
     */
    function getDevice(key) {
        return $.ajax({
            url: "/devices/device/" + key,
            type: "GET",
            datatype: "json",
        });
    }

    /**
     * Create a new device profile on the server.
     */
    function createDevice(data) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    let csrf = Cookies.get('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            }
        });

        return $.ajax({
            url: "/devices/device/",
            type: "POST",
            data: data,
            contentType: "application/json",
            datatype: "json",
        });
    }

    /**
     * Update an existing device profile on the server.
     */
    function updateDevice(key, data) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    let csrf = Cookies.get('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            }
        });

        return $.ajax({
            url: "/devices/device/" + key,
            type: "PATCH",
            data: data,
            contentType: "application/json",
            datatype: "json",
        });
    }

    /**
     * Delete the given device profile from the server.
     */
    function deleteDevice(key) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    let csrf = Cookies.get('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            }
        });

        return $.ajax({
            url: "/devices/device/" + key,
            type: "DELETE",
            datatype: "json",
        });
    }

    /**
     * Create default Repository and Yangset for
     * the given device profile from the server.
     */
    function createDefaultRepoAndYangset(key) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    let csrf = Cookies.get('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            }
        });

        let progressBarDiv = startProgress($(c.progress), "", "", "Creating Repository and Yangset for "+key) || $(c.progress);
        return $.ajax({
            url: "/devices/device-defaults/" + key,
            type: "GET",
            datatype: "json",
            success: function(retObj) {
                    stopProgress(progressBarDiv);
                },
                error: function(retObj) {
                    stopProgress(progressBarDiv);
                }
        });
    }

    /**
     * Get the list of existing device profiles and populate the given list.
     */
    function refreshDeviceList() {
        listDevices().then(function(response) {
            $(c.deviceList).empty();
            if (!response.devices || !response.devices.length) {
                $(c.deviceList).append(
                    "<li>No devices defined &mdash; why not add one?</li>");
                return;
            }
            for (let device of response.devices) {
                $(c.deviceList).append(
                    $("<li>").append(
                        $('<label class="radio radio--alt"' +
                          ' title="' + device.description + '">').append(
                            '<input type="radio" name="device"' +
                                ' value="' + device.key + '"' +
                                ' title="' + device.description + '">' +
                            '<span class="radio__input"></span>' +
                            '<span class="radio__label">' + device.name +
                            '</span>')
                    )
                );
            }
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };

    /**
     * Get the list of existing device profiles and populate the given menu.
     *
     * @param {selector} selector: The menu(s) to populate with device profiles
     * @param {str} selection: Device to autoselect from the populated menu, if any.
     */
    function refreshDeviceMenu(selector, selection="") {
        selector.empty();
        listDevices().then(function(response) {
            selector.append('<option value=""></option>');
            for (let device of response.devices) {
                selector.append('<option value="' + device.key + '">' +
                                device.name + '</option>');
            };
            selector.val(selection);
            selector.trigger("change");
            selector.children('option[value=""]').prop("disabled", true);
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    }

    /**
     * Pop up the dialog used for creating a new device or cloning existing one
     */
    function newDeviceDialog(deviceKey = null, creationCallback = null) {
        $.ajax({
            url: (deviceKey ? "/devices/clone/" + deviceKey : "/devices/new/"),
            type: "GET",
            success: function(response) {
                $(config.deviceDialog).dialog({ autoOpen: false });
                $(config.deviceDialog).html(response);
                setupDeviceDialog();
                /*
                 * If this is a clone, it will be pre-populated with the
                 * parent profile's name. Clear that out.
                 */
                $(config.deviceDialog).find("#ys-base-profile_name").val("");
                $(config.deviceDialog).dialog({
                    title: 'New Device Profile',
                    minWidth: 400,
                    width: 'auto',
                    maxHeight: $(window).height() * 0.9,
                    buttons: {
                        'Create Profile': function() {
                            createDevice(
                                encodeDeviceData("#ys-device-form")
                            ).then(function(retObj) {
                                $(config.deviceDialog).dialog('close');
                                if (creationCallback) {
                                    creationCallback();
                                }
                            }, function(retObj) {
                                let json = JSON.parse(retObj.responseText);
                                if (json.errors) {
                                    reportValidationErrors(json.errors);
                                } else {
                                    popDialog("Error " + retObj.status + ": " + retObj.statusText);
                                }
                            });
                        },
                        'Check Connectivity': function() {
                            checkDevice(
                                '',
                                encodeDeviceData("#ys-device-form")
                            ).then(function(retObj) {
                                ;
                            });
                        },
                        'Cancel': function() {
                            $(this).dialog('close');
                        },
                    }
                }).dialog("open");
            },
            error: function(retObj) {
                popDialog("Error " + retObj.status + ": " + retObj.statusText);
            }
        })
    };

    /**
     * Pop up the dialog used for editing an existing device
     */
    function editDeviceDialog(deviceKey) {
        if (!deviceKey) {
            popDialog("No device selected");
            return;
        }
        $.ajax({
            url: "/devices/edit/" + deviceKey,
            type: "GET",
            success: function(response) {
                $(config.deviceDialog).dialog({ autoOpen: false });
                $(config.deviceDialog).html(response);
                setupDeviceDialog();
                /* Disallow changing name of existing profile */
                $(config.deviceDialog + " #ys-base-profile_name")
                    .prop("readonly", true);
                $(config.deviceDialog).dialog({
                    title: 'Edit Device Profile',
                    minWidth: 400,
                    width: 'auto',
                    maxHeight: $(window).height() * 0.9,
                    buttons: {
                        'Save Changes': function() {
                            updateDevice(
                              deviceKey,
                              encodeDeviceData("#ys-device-form")
                            ).then(function(retObj) {
                                $(config.deviceDialog).dialog("close");
                            });
                      },
                        'Check Connectivity': function() {
                            checkDevice(
                                deviceKey,
                                encodeDeviceData("#ys-device-form")
                            ).then(function(retObj) {
                                ;
                            });
                        },
                        'Cancel': function() {
                            $(this).dialog('close');
                        },
                    }
                }).dialog("open");
                if ($('#ys-netconf-enabled').prop("checked") == true) {
                    netconf.startEndSession(deviceKey, 'end');
                }
            },
            error: function(retObj) {
                popDialog("Error " + retObj.status + ": " + retObj.statusText);
            }
        });
    };

    /**
     * Shared UI logic between newDeviceDialog and editDeviceDialog
     */
    function setupDeviceDialog() {
        /*
         * Refresh the validity of the given field after any change in inputs
         */
        $(c.deviceDialog + " :input").change(function() {
            $(this).removeClass("input--valid");
            if ($(this).val()) {
                $(this).removeClass("input--invalid-required");
            }
            $(this).removeClass("input--invalid");
            $(this).addClass("input--dirty");
        });

        /*
         * Toggling the "device supports PROTOCOL" checkbox will enable/disable
         * all fields under the given protocol as appropriate.
         * TODO: this is now #ys-FEATURE-enabled, not .ys-feature-support
         */
        $(".ys-feature-support").change(function() {
            /* Given name="foo", find all "foo-" inputs in this form */
            let proto_tag = $(this).attr("name") + '-';
            let feature_elements = $(this).parents('form')
                .find(':input[name^="' + proto_tag + '"]');

            feature_elements.prop("readonly", !(this.checked));
            feature_elements.prop("disabled", !(this.checked));
        });

        /*
         * Propagate base values to placeholders for non-base values
         */
        $(c.deviceDialog + ' [id^="ys-base-"]').change(function() {
            let tag = $(this).attr("name").replace(/^base-/, '-');
            let related_elements = $(this).parents('form')
                .find(':input[name$="' + tag + '"][name!="' +
                      $(this).attr('name') + '"]');
            let placeholder = $(this).val();
            if (!placeholder) {
                placeholder = "(same as base)";
            } else if (tag.includes("password")) {
                placeholder = "••••••••";
            }
            related_elements.attr("placeholder", placeholder);
        });

        /* Set up initial placeholders, if any */
        $.each($(c.deviceDialog + ' [id^="ys-base-"]'), function() {
            $(this).trigger("change");
        });
    }

    function sendFileType(profileName, fileData) {
        if (fileData) {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        let csrf = Cookies.get('csrftoken');
                        xhr.setRequestHeader("X-CSRFToken", csrf);
                    }
                }
            });

            $(c.progressBar).progressbar({value: false});

            return $.ajax({
                url: "/devices/upload/" + profileName,
                type: "POST",
                data: JSON.stringify(fileData),
                contentType: "application/json",
                datatype: "json",
                success: function(retObj) {
                    $(c.progressBar).progressbar("destroy");
                    clearValidationErrors();
                },
                error: function(retObj) {
                    $(c.progressBar).progressbar("destroy");
                    let json = JSON.parse(retObj.responseText);
                    if (json.errors) {
                        reportValidationErrors(json.errors);
                    } else {
                        popDialog("Error " + retObj.status + ": " + retObj.statusText);
                    }
                }
            });
        }
    }

    /**
     * Encode the inputs from the deviceDialog into a dictionary.
     * The structure of this object matches that returned by the server via
     * the getDevice() function.
     * Helper function to newDeviceDialog / editDeviceDialog / checkDevice
     */
    function encodeDeviceData(form) {
        let data = {};
        let fileData = {};
        $(form + " :input").each(function(i, input) {
            let input_name = $(input).attr("name");
            let split = input_name.split("-");
            let category = split[0];
            let name = split[1];
            let value = $(input).val();
            if (!data.hasOwnProperty(category)) {
                data[category] = {};
            }
            if ($(input).is(':file')) {
                if (input.files.length == 0) {
                    value = $(input).attr("replace");
                } else {
                    value = input.files[0].name;

                    input.files[0].text().then(function(text){
                        fileData['category'] = category;
                        fileData['file_name'] = input.files[0].name;
                        fileData['file_data'] = text;
                        fileData['file_replace'] = $(input).attr("replace");
                        sendFileType(data.base.profile_name, fileData);
                    });
                }
            }
            if ($(input).is(':checkbox')) {
                value = $(input).is(':checked');
            }
            if (split.length > 2) {
                // This element represents a dict key or value, like
                // "category-name-key-1" or "category-othername-value-13"
                let keyOrValue = split[2];
                let index = split[3];
                if (keyOrValue == "key" && value != "") {
                    if (!data[category].hasOwnProperty(name)) {
                        data[category][name] = {};
                    }
                    let keyValue = value;
                    let valueValue = $('[name="' + category + '-' + name + '-value-' + index + '"]').val();
                    data[category][name][keyValue] = valueValue;
                }
            } else if (value != "_placeholder_") {
                data[category][name] = value;
            }
        });
        return JSON.stringify(data);
    }

    /**
     * Check connectivity to a device and report results.
     *
     * @param {string} profileName
     * @param {string} requestData
     */
    function checkDevice(profileName, requestData=null) {
        if (!profileName && !requestData) {
            popDialog("No profile specified");
            return;
        }
        if (requestData) {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        let csrf = Cookies.get('csrftoken');
                        xhr.setRequestHeader("X-CSRFToken", csrf);
                    }
                }
            });
        }

        let output = $("<div>");
        $(c.progressBar).progressbar({value: false});

        return $.ajax({
            url: "/devices/check/" + profileName,
            type: requestData ? "POST" : "GET",
            data: requestData,
            contentType: "application/json",
            datatype: "json",
            success: function(retObj) {
                $(c.progressBar).progressbar("destroy");
                clearValidationErrors();
                output.append("<h4>Connectivity check results:</h4>");
                let results = $('<ul class="list--unstyled" style="white-space:pre">');
                for (var key in retObj) {
                    if (key == "status" || key == "os_type" || key == "os_ver") { continue; }
                    let entry = $("<li>").text(' ' + retObj[key].label);
                    if (retObj[key].status) {
                        entry.prepend('<span class="text-success icon icon-check-square">');
                    } else {
                        entry.prepend('<span class="text-danger icon icon-error">');
                        entry.append($('<ul class="text-small">')
                                     .append($('<li>').text(retObj[key].reason)));
                    }
                    results.append(entry);
                }
                output.append(results);
                if (profileName == ''){
                    var profile_name = JSON.parse(requestData)['base']['profile_name'];
                    profileName = profile_name
                }

                output.dialog({
                    title: 'Connectivity check results for "' + profileName + '"',
                    minWidth: 500,
                    width: 'auto',
                }).dialog("open");
                if (window.dataLayer) {
                    window.dataLayer.push ({
                        'os_type': retObj['os_type'],
                        'os_ver': retObj['os_ver']
                    });
                }
            },
            error: function(retObj) {
                $(c.progressBar).progressbar("destroy");
                let json = JSON.parse(retObj.responseText);
                if (json.errors) {
                    reportValidationErrors(json.errors);
                } else {
                    popDialog("Error " + retObj.status + ": " + retObj.statusText);
                }
            },
        });
    }

    /**
     * Helper function to newDeviceDialog and editDeviceDialog.
     * Clear out input validation error markup added by reportValidationErrors.
     */
    function clearValidationErrors() {
        /* Remove any existing error messages and highlighting*/
        $(".help-block").remove();
        $(".input--invalid").removeClass("input--invalid");
        $(".input--invalid-required").removeClass("input--invalid-required");
        /* Mark everything as valid until proven otherwise */
        $(":input").addClass("input--dirty");
        $(":input").addClass("input--valid");
    }

    /**
     * Helper function to newDeviceDialog and editDeviceDialog.
     * Apply appropriate markup to input fields that failed validation.
     */
    function reportValidationErrors(errors) {
        clearValidationErrors();

        $.each(errors, function(category, category_errors) {
            $.each(category_errors, function(key, value) {
                const input = $('[name="' + category + '-' + key + '"]');
                input.removeClass("input--valid");
                if (value == "This is a required field") {
                    input.addClass("input--invalid-required");
                    input.parent().after('<div class="help-block text-warning">' +
                                         '<span class="icon-exclamation-triangle"></span>' +
                                         '<span>' + value + '</span></div>');
                } else {
                    input.addClass("input--invalid");
                    input.parent().after('<div class="help-block text-danger">' +
                                         '<span class="icon-error"></span>' +
                                         '<span>' + value + '</span></div>');
                }
                input.parent().parent().addClass("form-group--helper");
            });
        });
        popDialog("Please correct validation errors and retry");
    }

    /* Public API */
    return {
        config: config,
        getDevice: getDevice,
        updateDevice: updateDevice,
        deleteDevice: deleteDevice,
        createDefaultRepoAndYangset: createDefaultRepoAndYangset,
        refreshDeviceList: refreshDeviceList,
        refreshDeviceMenu: refreshDeviceMenu,
        newDeviceDialog: newDeviceDialog,
        editDeviceDialog: editDeviceDialog,
        checkDevice: checkDevice,
    }
}();
