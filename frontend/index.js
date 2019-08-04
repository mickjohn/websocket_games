MODULUS = 97
BASE = 26
DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

MODULUS_TABLE = {
    0: 'redorblack'
}

function DecodeGameCode(game_code) {

    let index = game_code.length - 1;
    if (index < 0) {
        return null;
    }

    let decoded_number = 0;
    for (let posistion = 0; posistion < game_code.length; posistion++) {
        let index = game_code.length - posistion - 1;
        let digit = game_code[index];
        let number = DIGITS.indexOf(digit);
        decoded_number += (number * (BASE ** posistion));
    }

    return decoded_number;
}

function JoinGame(e) {
    let code = 0;
    let decoded_code = DecodeGameCode(code);

    if (decoded_code === null) {
        console.error('Could not decode game code');
        return null;
    }

    let mod = code % MODULUS;
    let game = MODULUS_TABLE[mod];
    console.info(`Joining ${game}`);
    let url = BuildUrl(game, code);
    window.location.href = url;
}

function BuildUrl(gamePath, gameCode) {
    let location = window.location;
    let protocol = location.protocol;
    let host = location.host;
    let url = `${protocol}//${host}/${gamePath}?gameCode=${gameCode}`;
    return url;
}