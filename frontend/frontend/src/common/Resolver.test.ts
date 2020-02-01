import * as resolver from './Resolver'

it('Can decode a game code', () => {
    // Red or black game code
    let code: string = "YKJT";
    let decoded: number = resolver.DecodeGameCode(code) || -1;
    expect(decoded).toEqual(428837);

    // When divided by the modulus, it should be 0
    expect(decoded % 97).toEqual(0);
});
