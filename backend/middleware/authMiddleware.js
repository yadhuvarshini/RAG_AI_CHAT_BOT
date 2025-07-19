
const express = require('express')

function extractToken(req, res, next){
    const authHeader = req.headers('authorization')
    if(authHeader && authHeader.startsWith('Bearer')){
        req.token = authHeader.split(' ')[1];
    } else {
        console.log("token error")
        req.token = null;
    }
    next();
}

module.exports = extractToken;