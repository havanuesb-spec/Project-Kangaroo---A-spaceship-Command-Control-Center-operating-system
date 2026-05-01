(function (global) {
    "use strict";

    var logic = global.PilotingLogic;

    if (!logic) {
        throw new Error("PilotingLogic is required before piloting-game.js");
    }

    var boardElement = document.getElementById("game-board");
    var overlayElement = document.getElementById("board-overlay");
    var scoreElement = document.getElementById("score-value");
    var beaconsElement = document.getElementById("beacons-value");
    var bestElement = document.getElementById("best-value");
    var statusElement = document.getElementById("flight-status");
    var launchButton = document.getElementById("launch-button");
    var restartButton = document.getElementById("restart-button");
    var controlButtons = document.querySelectorAll("[data-control]");
    var BEST_SCORE_KEY = "sky-pilot-best-score";
    var state = logic.createInitialState(Date.now());
    var bestScore = readBestScore();
    var cells = [];
    var timerId = 0;

    buildBoard();
    render();

    launchButton.addEventListener("click", function () {
        if (state.phase === "gameover") {
            state = logic.restartGame(Date.now());
        } else {
            state = logic.togglePause(state);
        }

        syncBestScore();
        render();
        scheduleTick(true);
    });

    restartButton.addEventListener("click", function () {
        state = logic.restartGame(Date.now());
        syncBestScore();
        render();
        scheduleTick(true);
    });

    controlButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            handleDirection(button.dataset.control);
        });
    });

    document.addEventListener("keydown", function (event) {
        var key = event.key.toLowerCase();
        var direction =
            {
                arrowup: "up",
                w: "up",
                arrowdown: "down",
                s: "down",
                arrowleft: "left",
                a: "left",
                arrowright: "right",
                d: "right"
            }[key];

        if (direction) {
            event.preventDefault();
            handleDirection(direction);
            return;
        }

        if (key === " " || key === "p") {
            event.preventDefault();

            if (state.phase === "gameover") {
                state = logic.restartGame(Date.now());
            } else {
                state = logic.togglePause(state);
            }

            render();
            scheduleTick(true);
            return;
        }

        if (key === "r") {
            event.preventDefault();
            state = logic.restartGame(Date.now());
            render();
            scheduleTick(true);
        }
    });

    function buildBoard() {
        var totalCells = logic.BOARD_WIDTH * logic.BOARD_HEIGHT;

        for (var index = 0; index < totalCells; index += 1) {
            var cell = document.createElement("div");
            cell.className = "cell";
            cell.setAttribute("role", "gridcell");
            boardElement.appendChild(cell);
            cells.push(cell);
        }
    }

    function handleDirection(direction) {
        if (state.phase === "gameover") {
            return;
        }

        if (state.phase === "ready" || state.phase === "paused") {
            state = logic.startGame(state);
        }

        state = logic.setQueuedMove(state, direction);
        render();
        scheduleTick();
    }

    function scheduleTick(resetTimer) {
        if (resetTimer && timerId) {
            global.clearTimeout(timerId);
            timerId = 0;
        }

        if (state.phase !== "running" || timerId) {
            return;
        }

        timerId = global.setTimeout(function () {
            timerId = 0;
            state = logic.stepGame(state);
            syncBestScore();
            render();
            scheduleTick();
        }, logic.getTickDelay(state));
    }

    function render() {
        var hazards = createKeySet(state.hazards);
        var beacons = createKeySet(state.beacons);
        var pilotKey = logic.toCellKey(state.pilot);

        scoreElement.textContent = String(state.score);
        beaconsElement.textContent = String(state.beaconsCollected);
        bestElement.textContent = String(bestScore);
        launchButton.textContent = getLaunchLabel(state.phase);
        statusElement.textContent = getStatusMessage();

        for (var y = 0; y < logic.BOARD_HEIGHT; y += 1) {
            for (var x = 0; x < logic.BOARD_WIDTH; x += 1) {
                var key = x + "," + y;
                var cell = cells[(y * logic.BOARD_WIDTH) + x];
                var className = "cell";

                if (hazards.has(key)) {
                    className += " cell--hazard";
                }

                if (beacons.has(key)) {
                    className += " cell--beacon";
                }

                if (pilotKey === key) {
                    className += " cell--pilot";

                    if (hazards.has(key)) {
                        className += " cell--crash";
                    }
                }

                cell.className = className;
            }
        }

        if (state.phase === "running") {
            overlayElement.hidden = true;
            return;
        }

        overlayElement.hidden = false;
        overlayElement.textContent = getOverlayMessage();
    }

    function createKeySet(points) {
        var keys = new Set();

        for (var index = 0; index < points.length; index += 1) {
            keys.add(logic.toCellKey(points[index]));
        }

        return keys;
    }

    function getLaunchLabel(phase) {
        if (phase === "running") {
            return "Pause";
        }

        if (phase === "gameover") {
            return "Launch Again";
        }

        return "Launch";
    }

    function getOverlayMessage() {
        if (state.phase === "paused") {
            return "Flight paused. Press Launch, Space, or a direction to continue.";
        }

        if (state.phase === "gameover") {
            return "Aircraft lost. Press Launch Again or Restart to try another run.";
        }

        return "Press Launch or use the controls to take off.";
    }

    function getStatusMessage() {
        if (state.phase === "paused") {
            return "Paused";
        }

        if (state.phase === "gameover") {
            return "Game over";
        }

        if (state.phase === "ready") {
            return "Ready for takeoff";
        }

        return "Flying through storm lane " + (state.distance + 1);
    }

    function readBestScore() {
        try {
            var storedValue = global.localStorage.getItem(BEST_SCORE_KEY);
            var parsed = Number.parseInt(storedValue || "0", 10);
            return Number.isFinite(parsed) ? parsed : 0;
        } catch (error) {
            return 0;
        }
    }

    function syncBestScore() {
        if (state.score <= bestScore) {
            return;
        }

        bestScore = state.score;

        try {
            global.localStorage.setItem(BEST_SCORE_KEY, String(bestScore));
        } catch (error) {
            return;
        }
    }
})(window);
