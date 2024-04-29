async function agreeSharedSecretKey() {
    let keyPair = await window.crypto.subtle.generateKey(
        {
        name: "ECDH",
        namedCurve: "P-384",
        },
        false,
        ["deriveBits"]
    );
    window.localStorage.setItem("keyPair", JSON.stringify(keyPair)) // save data to local storage

    // read data from localstorage
    let keyPairItem = window.localStorage.getItem("keyPair")
    console.log(JSON.parse(keyPairItem));
}
agreeSharedSecretKey();

