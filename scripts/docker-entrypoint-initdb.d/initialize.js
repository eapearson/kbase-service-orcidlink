// use admin
admindb = db.getSiblingDB('admin')
admindb.auth("dev_root", "dev_r00t")
// use orcidlink
orcidlink = db.getSiblingDB('orcidlink')
orcidlink.createUser({
    user: "dev",
    pwd: "d3v",
    roles: [{role: "readWrite", db: "orcidlink"}]

})
// mongosh < initialize.js