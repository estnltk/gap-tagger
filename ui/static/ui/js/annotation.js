function Timer() {
    var self = this;
    self.milliseconds = 0;
    self.timer;
    self.ontick_callback;
    self.pause = function () {
        clearInterval(self.timer);
    };
    self.resume = function () {
        self.start();
    };
    self.reset = function () {
        self.milliseconds = 0;
        if (self.timer != undefined)
            clearInterval(self.timer);
        self.start();
    };
    self.start = function () {
        self.timer = setInterval(function () {
            self.milliseconds += 100;
            if (self.ontick_callback != undefined)
                self.ontick_callback(self.milliseconds);
        }, 100);
    };
    self.ontick = function (callback) {
        self.ontick_callback = callback;
    };
}

function View() {
    var self = this;
    self.set_controller = function (controller) {
        self.controller = controller;
        $('.btn-variant').click(function () {
            var is_correct = $(this).attr("data-correct") == "true";
            var both_fit = $(this).attr("data-both-fit") == "true";
            controller.annotate_sentence(is_correct, both_fit);
        });
        $('#btn-timer').click(function () {
            if ($('#btn-timer').attr("data-action") == "resume") {
                $('#btn-timer .glyphicon').removeClass('glyphicon-play');
                $('#btn-timer .glyphicon').addClass('glyphicon-pause');
                $('#btn-timer').attr("data-action", "pause");
                controller.resume_timer();
            }
            else { // pause
                $('#btn-timer .glyphicon').removeClass('glyphicon-pause');
                $('#btn-timer .glyphicon').addClass('glyphicon-play');
                $('#btn-timer').attr("data-action", "resume");
                controller.pause_timer();
            }
        });
        $("body").keypress(function (e) {
            var btn;
            if (e.which == 97) // a
                btn = $('#variant-btn-1');
            else if (e.which == 115) // s
                btn = $('#variant-btn-both-1');
            else if (e.which == 100) // d
                btn = $('#variant-btn-both-2');
            else if (e.which == 102) // f
                btn = $('#variant-btn-2');

            if (btn != undefined) {
                btn.addClass("active");
                btn.trigger("click");
                setTimeout(function () {
                    btn.removeClass("active").removeClass("focus");
                }, 150);
            }
        });
    };
    self.update = function (state) {
        var snt = state.get_current_sentence();
        var marked_sentence = annotate_entity_in_sentence(snt['sentence'], snt['gap_start'], snt['gap_end']);
        $('#sentence').html(marked_sentence);

        if (Math.random() < 0.5) {
            $('#variant-btn-1').attr('data-correct', true).find('.lbl').html(snt['gap_correct']);
            $('#variant-btn-2').attr('data-correct', false).find('.lbl').html(snt['gap_variant']);
            $('#variant-btn-both-1').attr({'data-correct': true, 'data-both-fit': true});
            $('#variant-btn-both-2').attr({'data-correct': false, 'data-both-fit': true});
        }
        else {
            $('#variant-btn-1').attr('data-correct', false).find('.lbl').html(snt['gap_variant']);
            $('#variant-btn-2').attr('data-correct', true).find('.lbl').html(snt['gap_correct']);
            $('#variant-btn-both-1').attr({'data-correct': false, 'data-both-fit': true});
            $('#variant-btn-both-2').attr({'data-correct': true, 'data-both-fit': true});
        }
    };
    self.update_time = function (msecs) {
        /* Update displayed time every second */
        $('#timer').html(Math.floor(msecs / 1000));
    }
}

function annotate_entity_in_sentence(snt, gap_start, gap_end) {
    // "Tallinn on Eesti pealinn ." -> "Tallinn on <span>...</span> pealinn ."
    return snt.substring(0, gap_start) + '<span class="snt-gap">...</span>' + snt.substring(gap_end, snt.length);
}

function State(sentences, cur_snt) {
    var self = this;
    self.sentences = sentences;
    self.cur_snt = cur_snt;
    self.reset = function () {
        self.cur_snt = 0;
        self.sentences = [];
    };
    self.get_current_sentence = function () {
        return self.sentences[self.cur_snt];
    };
    self.increment = function () {
        self.cur_snt += 1;
    };
    self.is_last_sentence = function () {
        return self.cur_snt == self.sentences.length - 1;
    };
    self.annotate_sentence = function (is_correct_variant_selected, both_fit, time) {
        var snt = self.sentences[self.cur_snt];
        snt["correct_variant_selected"] = is_correct_variant_selected;
        snt["both_variants_fit"] = both_fit;
        snt["time"] = time;
    };
}

function Controller() {
    var self = this;
    self.timer = new Timer();
    self.timer.ontick(function (s) {
        if (self.view != undefined)
            self.view.update_time(s);
    });
    self.set_view = function (view) {
        self.view = view;
    };
    self.pause_timer = function () {
        self.timer.pause();
    };
    self.resume_timer = function () {
        self.timer.resume();
    };
    self.load_data = function () {
        $.ajax({
                url: '/load-sentences-view/',
                method: 'post',
                data: {'corpus_id': get_corpus_id_from_url()},
                cache: false
            })
            .done(self.data_loaded)
            .fail(function (err) {
                alert(err['statusText']);
            });
    };
    self.data_loaded = function (data) {
        if (data.length == 0) {
            alert('Terve korpus on märgendatud!');
            window.location = '/';
        }
        else {
            self.state = new State(data, 0);
            self.view.update(self.state);
            self.timer.reset();
        }
    };
    self.pick_next_sentence = function () {
        if (self.state.is_last_sentence()) {
            var snts = _.map(self.state.sentences, function (s) {
                return {
                    "id": s['id'],
                    "correct_variant_selected": s["correct_variant_selected"],
                    "both_variants_fit": s["both_variants_fit"] == true,
                    "time": s["time"],
                    "corpus_id": get_corpus_id_from_url()
                };
            });
            self.state.reset();
            $.ajax({
                url: '/submit-sentences-view/',
                method: 'post',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(snts)
            }).fail(function (err) {
                alert('Failed to submit word data. Error: ' + err["status"] + ' ' + err["statusText"]);
            }).done(self.data_loaded);
        }
        else {
            self.state.increment();
            self.view.update(self.state);
            self.timer.reset();
        }
    };
    self.annotate_sentence = function (is_correct, both_fit) {
        self.timer.pause();
        self.view.update_time(0);
        self.state.annotate_sentence(is_correct, both_fit, self.timer.milliseconds);
        self.pick_next_sentence();
    };
    self.set_both_variants_fit = function (do_fit) {
        self.state.set_both_variants_fit(do_fit);
    };
}

function get_corpus_id_from_url() {
    var corpus_id_regexp = /(\d+)\/?$/;
    var match = corpus_id_regexp.exec(window.location.href);
    var corpus_id = match[1];
    return corpus_id;
}

$(document).ready(function () {
    var view = new View();
    var controller = new Controller();
    view.set_controller(controller);
    controller.set_view(view);
    controller.load_data();
});
