define("ace/mode/pddl_highlight_rules", ["require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"], function (require, exports, module) {

    "use strict";
    var oop = require("../lib/oop");
    var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;
    var PDDLHighlightRules = function () {

        this.$rules =
            {
                "start": [{
                    token: 'variable.other',
                    regex: '\\?([A-Za-z0-9]|-|_)+'
                },
                    {
                        token: 'constant.numeric',
                        regex: '\\b((0(x|X)[0-9a-fA-F]*)|(([0-9]+\\.?[0-9]*)|(\\.[0-9]+))((e|E)(\\+|-)?[0-9]+)?)(L|l|UL|ul|u|U|F|f|ll|LL|ull|ULL)?\\b'
                    },
                    {
                        token: 'keyword.other',
                        regex: ':(strips|typing|negative-preconditions|disjunctive-preconditions|equality|existential-preconditions|universal-preconditions|quantified-preconditions|conditional-effects|fluents|numeric-fluents|object-fluents|adl|durative-actions|duration-inequalities|continuous-effects|derived-predicates|timed-initial-literals|preferences|constraints|action-costs)'
                    },
                    {
                        caseInsensitive: true,
                        token: 'storage.type',
                        regex: ':(requirements|types|constants|predicates|functions|action|init|goal|objects|domain)'
                    },
                    {
                        token: 'support.function',
                        regex: '(assign|scale-up|scale-down|increase|decrease)'
                    },
                    {
                        token: 'constant.language',
                        regex: '\\b(start|end|all|define)\\b'
                    },
                    {
                        caseInsensitive: true,
                        token: 'keyword.operator',
                        regex: '\\b(?:eq|neq|when|and|or)\\b'
                    },
                    {
                        caseInsensitive: true,
                        token: 'keyword.operator',
                        regex: ':(parameters|duration|condition|effect|precondition)'
                    },
                    {
                        token: 'comment',
                        regex: ";.*$"
                    }
                ]

            };
        this.normalizeRules();
    };
    oop.inherits(PDDLHighlightRules, TextHighlightRules);
    exports.PDDLHighlightRules = PDDLHighlightRules;

});

define("ace/mode/folding/pddl_style", ["require", "exports", "module", "ace/lib/oop", "ace/range", "ace/mode/folding/fold_mode"], function (require, exports, module) {
    "use strict";
    var oop = require("../../lib/oop");
    var Range = require("../../range").Range;
    var BaseFoldMode = require("./fold_mode").FoldMode;

    var FoldMode = exports.FoldMode = function (commentRegex) {
        if (commentRegex) {
            this.foldingStartMarker = new RegExp(
                this.foldingStartMarker.source.replace(/\|[^|]*?$/, "|" + commentRegex.start)
            );
            this.foldingStopMarker = new RegExp(
                this.foldingStopMarker.source.replace(/\|[^|]*?$/, "|" + commentRegex.end)
            );
        }
    };
    oop.inherits(FoldMode, BaseFoldMode);

    (function () {

        //this.foldingStartMarker = /(\{|\[)[^\}\]]*$|^\s*(\/\*)/;
        //this.foldingStopMarker = /^[^\[\{]*(\}|\])|^[\s\*]*(\*\/)/;

        this.foldingStartMarker = /(\()[^\)]*$/;
        this.foldingStopMarker = /^[^\(]*(\))/;

        this.getFoldWidgetRange = function (session, foldStyle, row, forceMultiline) {
            var line = session.getLine(row);
            var match = line.match(this.foldingStartMarker);
            if (match) {
                var i = match.index;

                if (match[1])
                    return this.openingBracketBlock(session, match[1], row, i);

                var range = session.getCommentFoldRange(row, i + match[0].length, 1);

                if (range && !range.isMultiLine()) {
                    if (forceMultiline) {
                        range = this.getSectionRange(session, row);
                    } else if (foldStyle !== "all")
                        range = null;
                }

                return range;
            }

            if (foldStyle === "markbegin")
                return;

            match = line.match(this.foldingStopMarker);
            if (match) {
                i = match.index + match[0].length;

                if (match[1])
                    return this.closingBracketBlock(session, match[1], row, i);

                return session.getCommentFoldRange(row, i, -1);
            }
        };

        this.getSectionRange = function (session, row) {
            var line = session.getLine(row);
            var startIndent = line.search(/\S/);
            var startRow = row;
            var startColumn = line.length;
            row = row + 1;
            var endRow = row;
            var maxRow = session.getLength();
            while (++row < maxRow) {
                line = session.getLine(row);
                var indent = line.search(/\S/);
                if (indent === -1)
                    continue;
                if (startIndent > indent)
                    break;
                var subRange = this.getFoldWidgetRange(session, "all", row);

                if (subRange) {
                    if (subRange.start.row <= startRow) {
                        break;
                    } else if (subRange.isMultiLine()) {
                        row = subRange.end.row;
                    } else if (startIndent == indent) {
                        break;
                    }
                }
                endRow = row;
            }

            return new Range(startRow, startColumn, endRow, session.getLine(endRow).length);
        };

    }).call(FoldMode.prototype);

});



define("ace/mode/matching_brace_outdent", ["require", "exports", "module", "ace/range"], function (require, exports, module) {
    "use strict";
    var Range = require("../range").Range;

    var MatchingBraceOutdent = function () {
    };

    (function () {

        this.checkOutdent = function (line, input) {
            if (!/^\s+$/.test(line))
                return false;

            return /^\s*\}/.test(input);
        };

        this.autoOutdent = function (doc, row) {
            var line = doc.getLine(row);
            var match = line.match(/^(\s*\})/);

            if (!match) return 0;

            var column = match[1].length;
            var openBracePos = doc.findMatchingBracket({row: row, column: column});

            if (!openBracePos || openBracePos.row === row) return 0;

            var indent = this.$getIndent(doc.getLine(openBracePos.row));
            doc.replace(new Range(row, 0, row, column - 1), indent);
        };

        this.$getIndent = function (line) {
            return line.match(/^\s*/)[0];
        };

    }).call(MatchingBraceOutdent.prototype);

    exports.MatchingBraceOutdent = MatchingBraceOutdent;
});


define("ace/mode/pddl", ["require", "exports", "module", "ace/lib/oop", "ace/mode/text", "ace/mode/pddl_highlight_rules", "ace/mode/folding/pddl_style", "ace/mode/matching_brace_outdent"], function (require, exports, module) {/*

*/
    "use strict";
    var oop = require("../lib/oop");
    var TextMode = require("./text").Mode;
    var PDDLHighlightRules = require("./pddl_highlight_rules").PDDLHighlightRules;
    var PDDLFoldMode = require("./folding/pddl_style").FoldMode;
    var MatchingBraceOutdent = require("./matching_brace_outdent").MatchingBraceOutdent;



    var Mode = function () {
        this.$outdent = MatchingBraceOutdent();
        this.HighlightRules = PDDLHighlightRules;
        this.$behaviour = this.$defaultBehaviour;
        this.foldingRules = new PDDLFoldMode();
    };
    oop.inherits(Mode, TextMode);
    (function () {
        this.lineCommentStart = ";";
        this.$id = "ace/mode/pddl";
    }).call(Mode.prototype);
    exports.Mode = Mode;

});
(function () {
    window.require(["ace/mode/pddl"], function (m) {
        if (typeof module == "object" && typeof exports == "object" && module) {
            module.exports = m;
        }
    });
})();
