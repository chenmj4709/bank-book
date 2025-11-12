import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

// 获取当前文件的目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 创建 require 函数以导入 JSON
const require = createRequire(import.meta.url);
const pkg = require('../package.json');

// 读取 web/package.json
const webPkgPath = path.resolve(__dirname, '../web/package.json');
const webPkg = JSON.parse(fs.readFileSync(webPkgPath, 'utf8'));

// 更新版本号
webPkg.version = pkg.version;

fs.writeFileSync(webPkgPath, JSON.stringify(webPkg, null, 2), 'utf8');