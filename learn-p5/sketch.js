var state = {};
state.hsb = [0, 0, 0];
state.pastHsb = state.hsb;
state.filterCoef = [0.99, 0.01]
state.hsbRanges = [[0,360], [40,60], [40,60]];
state.frameRate = 60;

function setup() {
    createCanvas(windowWidth, windowHeight);
    colorMode(HSB);
    frameRate(state.frameRate);
}

function draw() {
    // Debug
    print(state);

    // Update hsb based on random target
    state.hsb[0] = state.hsb[0] * state.filterCoef[0] +
                   random(state.hsbRanges[0][0], state.hsbRanges[0][1]) * state.filterCoef[1];
    state.hsb[1] = state.hsb[1] * state.filterCoef[0] +
                   random(state.hsbRanges[1][0], state.hsbRanges[1][1]) * state.filterCoef[1];
    state.hsb[2] = state.hsb[2] * state.filterCoef[0] +
                   random(state.hsbRanges[2][0], state.hsbRanges[2][1]) * state.filterCoef[1];

    // Draw
    background(state.hsb[0], state.hsb[1], state.hsb[2]);
}

function randomHsb(ranges) {
    return [random(ranges[0][0], ranges[0][1]),
            random(ranges[1][0], ranges[1][1]),
            random(ranges[2][0], ranges[2][1])];
}