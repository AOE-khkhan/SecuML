function createTrainTestMonitoring(child_exp_id, train_test, with_alerts) {
    var panel_title = '';
    var div = null;
    if (train_test == 'cv') {
        panel_title = 'Cross Validation';
        div = cleanDiv('train');
    } else {
        panel_title = upperCaseFirst(train_test);
        div = cleanDiv(train_test);
    }
    var href = null;
    if (train_test != 'cv') {
        href = '/SecuML/' + child_exp_id;
    }
    var panel = createPanel('panel-primary', null,
                            panel_title + ' Performance', div, null,
                            true, href);
    var monitoring = panel[0];
    var heading = panel[1];
    if (train_test != 'cv') {
        displayDetectionExecTime(child_exp_id, heading);
    }
    createDivWithClass(train_test + '_monitoring', 'tabbable boxed parentTabs',
                       monitoring);
    if (train_test == 'test' && with_alerts) {
        createDivWithClass('alerts_buttons', 'col-md-12', monitoring);
        if (! children_exps[child_exp_id].multiclass) {
            displayAlertsButtons(child_exp_id);
        }
    }
}

function displayDetectionExecTime(child_exp_id, heading) {
    var query = buildQuery('supervisedLearningMonitoring', [child_exp_id,
                                                            'exec_time']);
    $.getJSON(query, function(data) {
        var exec_time = (data.predictions / data.num_instances) * 1000;
        heading.textContent += ' (' + exec_time.toFixed(3) + ' ms / instance)'
    });
}

function displayAlertsButton(buttons_group, button_label, buttons_title,
                             child_exp_id, clustering_exp_id) {
    var label_group = createDivWithClass(null, 'btn-group',
                                         parent_div=buttons_group);
    var label_button = document.createElement('button');
    label_button.setAttribute('class', 'btn btn-danger');
    label_button.setAttribute('type', 'button');
    label_button.setAttribute('id', button_label + '_button');
    var label_button_text = document.createTextNode(buttons_title);
    label_button.appendChild(label_button_text);
    label_button.addEventListener('click', function() {
        if (button_label != 'clustering') {
            var query = buildQuery('alerts', [child_exp_id, button_label]);
            window.open(query);
        } else {
            var query = buildQuery('SecuML', [clustering_exp_id]);
            window.open(query);
        }
    });
    label_group.appendChild(label_button);
}

function displayAlertsButtons(child_exp_id) {
    var div = document.getElementById('alerts_buttons');
    var alerts_div = createPanel('panel-danger', null, 'Alerts Analysis', div);
    var buttons_group = createDivWithClass(null,
                                           'btn-group btn-group-justified',
                                           parent_div=alerts_div);
    var labels = ['topN', 'random'];
    var titles = ['Top N', 'Random'];
    var clustering_exp_id = getAlertsClusteringExpId(child_exp_id);
    if (clustering_exp_id) {
        labels.push('clustering');
        titles.push('Clustering');
    }
    for (var i = 0; i < labels.length; i++) {
        displayAlertsButton(buttons_group, labels[i], titles[i], child_exp_id,
                            clustering_exp_id);
    }
}

function displayDetectionMonitoring(conf, train_test, fold_id,
                                    test_dataset='None') {
  d3.json(buildQuery('getDiademDetectionChildExp',
                     [conf.exp_id, train_test, fold_id, test_dataset]),
          function(exp_info) {
              var child_exp_id = exp_info.exp_id;
              children_exps[child_exp_id] = exp_info;
              createTrainTestMonitoring(child_exp_id, train_test,
                                        test_dataset!='all');
              displayMonitoringTabs(train_test, child_exp_id, exp_info);
              updateMonitoringDisplay(train_test, child_exp_id, exp_info.proba,
                                      exp_info.with_scoring,
                                      exp_info.multiclass,
                                      exp_info.perf_monitoring,
                                      test_dataset!='all');
          });
}

function updateMonitoringDisplay(train_test, child_exp_id, proba, with_scoring,
                                 multiclass, perf_monitoring, with_links) {
    updatePredictionsDisplay(train_test, child_exp_id, with_links);
    if (perf_monitoring) {
        updatePerformanceDisplay(train_test, child_exp_id, proba, with_scoring,
                                 multiclass, with_links);
    }
}

function displayMonitoringTabs(train_test, child_exp_id, exp_info) {
    var tabs_div = document.getElementById(train_test + '_monitoring');;
    var menu_titles = [];
    var menu_labels = [];
    if (exp_info.perf_monitoring) {
        menu_titles.push('Performance');
        menu_labels.push(train_test + '_perf');
    }
    menu_titles.push('Predictions');
    menu_labels.push(train_test + '_pred');
    var menu = createTabsMenu(menu_labels, menu_titles, tabs_div,
                              train_test + '_monitoring_tabs');
    if (exp_info.perf_monitoring) {
        displayPerformanceTabs(train_test, exp_info);
    }
}
