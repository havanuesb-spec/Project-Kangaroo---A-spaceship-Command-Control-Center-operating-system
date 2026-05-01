(function (global) {
    "use strict";

    var BOARD_WIDTH = 9;
    var BOARD_HEIGHT = 14;
    var GAP_WIDTH = 3;
    var START_X = Math.floor(BOARD_WIDTH / 2);
    var START_Y = BOARD_HEIGHT - 3;
    var NO_MOVE = "none";
    var MOVE_DELTAS = {
        up: { x: 0, y: -1 },
        down: { x: 0, y: 1 },
        left: { x: -1, y: 0 },
        right: { x: 1, y: 0 },
        none: { x: 0, y: 0 }
    };

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function normalizeSeed(seed) {
        var numericSeed = Number.isFinite(seed) ? seed : Date.now();
        return (numericSeed >>> 0) || 1;
    }

    function nextRandom(seed) {
        var nextSeed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
        return {
            seed: nextSeed,
            value: nextSeed / 4294967296
        };
    }

    function toCellKey(point) {
        return point.x + "," + point.y;
    }

    function movePilot(pilot, direction) {
        var delta = MOVE_DELTAS[direction] || MOVE_DELTAS.none;

        return {
            x: clamp(pilot.x + delta.x, 0, BOARD_WIDTH - 1),
            y: clamp(pilot.y + delta.y, 0, BOARD_HEIGHT - 1)
        };
    }

    function shiftPoints(points) {
        return points
            .map(function (point) {
                return { x: point.x, y: point.y + 1 };
            })
            .filter(function (point) {
                return point.y < BOARD_HEIGHT;
            });
    }

    function resolveContacts(pilot, hazards, beacons) {
        var pilotKey = toCellKey(pilot);
        var collected = 0;
        var remainingBeacons = [];
        var hitHazard = false;

        for (var index = 0; index < hazards.length; index += 1) {
            if (toCellKey(hazards[index]) === pilotKey) {
                hitHazard = true;
                break;
            }
        }

        for (var beaconIndex = 0; beaconIndex < beacons.length; beaconIndex += 1) {
            if (toCellKey(beacons[beaconIndex]) === pilotKey) {
                collected += 1;
            } else {
                remainingBeacons.push(beacons[beaconIndex]);
            }
        }

        return {
            collected: collected,
            hitHazard: hitHazard,
            beacons: remainingBeacons
        };
    }

    function buildSpawnRow(previousCenter, seed) {
        var centerRoll = nextRandom(seed);
        var shift = Math.floor(centerRoll.value * 3) - 1;
        var nextCenter = clamp(previousCenter + shift, 1, BOARD_WIDTH - 2);
        var gapStart = nextCenter - Math.floor(GAP_WIDTH / 2);
        var gapEnd = gapStart + GAP_WIDTH - 1;
        var hazards = [];
        var beacons = [];
        var currentSeed = centerRoll.seed;
        var beaconRoll = nextRandom(currentSeed);

        currentSeed = beaconRoll.seed;

        for (var x = 0; x < BOARD_WIDTH; x += 1) {
            if (x < gapStart || x > gapEnd) {
                hazards.push({ x: x, y: 0 });
            }
        }

        if (beaconRoll.value > 0.58) {
            var laneRoll = nextRandom(currentSeed);
            currentSeed = laneRoll.seed;

            beacons.push({
                x: gapStart + Math.floor(laneRoll.value * GAP_WIDTH),
                y: 0
            });
        }

        return {
            corridorCenter: nextCenter,
            hazards: hazards,
            beacons: beacons,
            seed: currentSeed
        };
    }

    function createInitialState(seed) {
        return {
            width: BOARD_WIDTH,
            height: BOARD_HEIGHT,
            pilot: { x: START_X, y: START_Y },
            hazards: [],
            beacons: [],
            score: 0,
            beaconsCollected: 0,
            distance: 0,
            tick: 0,
            phase: "ready",
            queuedMove: NO_MOVE,
            corridorCenter: START_X,
            seed: normalizeSeed(seed)
        };
    }

    function setQueuedMove(state, direction) {
        if (!MOVE_DELTAS[direction]) {
            return state;
        }

        return Object.assign({}, state, {
            queuedMove: direction
        });
    }

    function startGame(state) {
        if (state.phase === "running") {
            return state;
        }

        return Object.assign({}, state, {
            phase: "running"
        });
    }

    function pauseGame(state) {
        if (state.phase !== "running") {
            return state;
        }

        return Object.assign({}, state, {
            phase: "paused"
        });
    }

    function togglePause(state) {
        if (state.phase === "running") {
            return pauseGame(state);
        }

        if (state.phase === "paused" || state.phase === "ready") {
            return startGame(state);
        }

        return state;
    }

    function restartGame(seed) {
        var restarted = createInitialState(seed);
        restarted.phase = "running";
        return restarted;
    }

    function endGame(state, pilot, hazards, beacons) {
        return Object.assign({}, state, {
            pilot: pilot,
            hazards: hazards,
            beacons: beacons,
            phase: "gameover",
            queuedMove: NO_MOVE
        });
    }

    function stepGame(state) {
        if (state.phase !== "running") {
            return state;
        }

        var movedPilot = movePilot(state.pilot, state.queuedMove);
        var firstPass = resolveContacts(movedPilot, state.hazards, state.beacons);

        if (firstPass.hitHazard) {
            return endGame(state, movedPilot, state.hazards, firstPass.beacons);
        }

        var shiftedHazards = shiftPoints(state.hazards);
        var shiftedBeacons = shiftPoints(firstPass.beacons);
        var spawnRow = buildSpawnRow(state.corridorCenter, state.seed);
        var hazards = shiftedHazards.concat(spawnRow.hazards);
        var beacons = shiftedBeacons.concat(spawnRow.beacons);
        var secondPass = resolveContacts(movedPilot, hazards, beacons);

        if (secondPass.hitHazard) {
            return endGame(state, movedPilot, hazards, secondPass.beacons);
        }

        var totalCollected = firstPass.collected + secondPass.collected;

        return {
            width: state.width,
            height: state.height,
            pilot: movedPilot,
            hazards: hazards,
            beacons: secondPass.beacons,
            score: state.score + 1 + (totalCollected * 4),
            beaconsCollected: state.beaconsCollected + totalCollected,
            distance: state.distance + 1,
            tick: state.tick + 1,
            phase: "running",
            queuedMove: NO_MOVE,
            corridorCenter: spawnRow.corridorCenter,
            seed: spawnRow.seed
        };
    }

    function getTickDelay(state) {
        var speedStep = Math.floor(state.distance / 12);
        return Math.max(120, 260 - (speedStep * 15));
    }

    var api = {
        BOARD_WIDTH: BOARD_WIDTH,
        BOARD_HEIGHT: BOARD_HEIGHT,
        createInitialState: createInitialState,
        setQueuedMove: setQueuedMove,
        startGame: startGame,
        pauseGame: pauseGame,
        togglePause: togglePause,
        restartGame: restartGame,
        stepGame: stepGame,
        getTickDelay: getTickDelay,
        toCellKey: toCellKey,
        buildSpawnRow: buildSpawnRow
    };

    global.PilotingLogic = api;

    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== "undefined" ? globalThis : this);
