admindb = db.getSiblingDB('admin')
admindb.auth("dev_root", "dev_r00t")
orcidlink = db.getSiblingDB('orcidlink')
orcidlink.createUser({
    user: "dev",
    pwd: "d3v",
    roles: [{role: "dbOwner", db: "orcidlink"}]
})

// The following code can be un-commented to
// simulate whatever starting condition you like,
// although it is better to use the migration script
// to do the heavy lifting.
// orcidlink.createCollection('description')
// description = orcidlink.getCollection('description')
// description.insertOne({
//     version: '0.2.1',
//     at: Date.now(),
//     migrated: false
// })
