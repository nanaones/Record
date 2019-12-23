
## SyntaxError: Invalid regular expression: /(.*\\__fixtures__\\.*|node_modules[\\\]react[\\\]dist[\\\].*|website\\node_modules\\.*|heapCapture\\bundle\.js|.*\\__tests__\\.*)$/: Unterminated character class


```
PS C:\Users\nanaones\SomeApp\ReactApplication\SomeApp> yarn start
yarn run v1.21.1
$ expo start
Starting project at C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck
Expo DevTools is running at http://localhost:19003
Opening DevTools in the browser... (press shift-d to disable)
error Invalid regular expression: /(.*\\__fixtures__\\.*|node_modules[\\\]react[\\\]dist[\\\].*|website\\node_modules\\.*|heapCapture\\bundle\.js|.*\\__tests__\\.*)$/: Unterminated character class. Run CLI with --verbose flag for more details.

SyntaxError: Invalid regular expression: /(.*\\__fixtures__\\.*|node_modules[\\\]react[\\\]dist[\\\].*|website\\node_modules\\.*|heapCapture\\bundle\.js|.*\\__tests__\\.*)$/: Unterminated character class
    at new RegExp (<anonymous>)
    at blacklist (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\metro-config\src\defaults\blacklist.js:34:10)
    at getBlacklistRE (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\@react-native-community\cli\build\tools\loadMetroConfig.js:66:59)
    at getDefaultConfig (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\@react-native-community\cli\build\tools\loadMetroConfig.js:82:20)
    at load (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\@react-native-community\cli\build\tools\loadMetroConfig.js:118:25)
    at Object.runServer [as func] (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\@react-native-community\cli\build\commands\server\runServer.js:82:58)
    at Command.handleAction (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\@react-native-community\cli\build\index.js:164:23)
    at Command.listener (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\commander\index.js:315:8)
    at Command.emit (events.js:210:5)
    at Command.parseArgs (C:\Users\nanaones\Documents\99_Git\App\ReactApplication\BodyCheck\node_modules\commander\index.js:651:12)
Metro Bundler process exited with code 1
Set EXPO_DEBUG=true in your env to view the stack trace.
error Command failed with exit code 1.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
```


```ini
[System]

OS: windows10 Pro 64 Bit

[Installed]

Yarn: v1.21.1
Node: v12.14.0
npm: 6.13.4
react-native: 0.61.0
```


`$ yarn start` 명령어로 Reactnative프로젝트를 실행할 때 위와같은 문제를 겪을경우, 
Windows 를 사용하고 있다면, 다음과 같은 경로 파일에 *`\`의 추가로 문제를 해결할 수 있다.* 

`ReactNativeRootPath/node_modules/metro-config/src/dafaults/blacklist.js`

```Js
var sharedBlacklist = [
  /node_modules[/\\]react[/\\]dist[\/\\].*/,
  /website\/node_modules\/.*/,
  /heapCapture\/bundle\.js/,
  /.*\/__tests__\/.*/
];
```

```Js
var sharedBlacklist = [
  /node_modules[\/\\]react[\/\\]dist[\/\\].*/,
  /website\/node_modules\/.*/,
  /heapCapture\/bundle\.js/,
  /.*\/__tests__\/.*/
];
```

Blacklist 를 통해서 이중으로 인식되는 상황을 막아주기 위한 BlackList 이지만, Windows에서는 경로 표현이 서로 다르므로, 적용되지 않아서 발생되는 문제이다.


---

