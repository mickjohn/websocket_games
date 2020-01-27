
function vibrate(pattern: number | number[]) {
    if (window.navigator.vibrate !== undefined) {
        window.navigator.vibrate(pattern);
    }
}

export default vibrate;