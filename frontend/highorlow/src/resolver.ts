let MODULUS: number = 97;
let BASE: number = 26;
let DIGITS: string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

let MODULUS_TABLE: Map<number, string> = new Map();
MODULUS_TABLE.set(0, 'highorlow');

export function DecodeGameCode(game_code: string) {

    let index: number = game_code.length - 1;
    if (index < 0) {
        return null;
    }

    let decoded_number: number = 0;
    for (let posistion = 0; posistion < game_code.length; posistion++) {
        let index: number = game_code.length - posistion - 1;
        let digit: string = game_code[index];
        let number: number = DIGITS.indexOf(digit);
        decoded_number += (number * (BASE ** posistion));
    }

    return decoded_number;
}

export default (DecodeGameCode);