import AppKit
import Carbon
import Darwin
import SwiftUI

private struct DesktopConfig: Decodable {
    let projectRoot: String
    let indexDirectory: String
    let backend: String
    let rerank: Bool
    let port: Int

    static func load() throws -> DesktopConfig {
        guard let url = Bundle.main.url(forResource: "desktop", withExtension: "json") else {
            throw DesktopError.message("缺少桌面配置，请重新运行 build.sh。")
        }
        return try JSONDecoder().decode(DesktopConfig.self, from: Data(contentsOf: url))
    }
}

private enum DesktopError: LocalizedError {
    case message(String)

    var errorDescription: String? {
        if case .message(let text) = self { return text }
        return nil
    }
}

private struct Health: Decodable {
    let backend: String
    let chunks: Int
    let sources: Int
    let assistant: AssistantInfo?
}

private struct AssistantInfo: Decodable {
    let model: String
}

private struct WarmupResponse: Decodable {
    let ready: Bool
}

private struct ChatCitation: Decodable, Identifiable {
    let citation_id: String
    let source: String
    let locator: String
    let content: String

    var id: String { citation_id }
}

private struct ChatResponse: Decodable {
    let conversation_id: String
    let answer: String
    let citations: [ChatCitation]
    let status: String
}

private struct StoredConversation: Decodable {
    let turns: [StoredTurn]
}

private struct StoredTurn: Decodable {
    let role: String
    let content: String
    let citations: [ChatCitation]
}

private struct ChatMessage: Identifiable {
    let id = UUID()
    let role: String
    let content: String
    let citations: [ChatCitation]
}

private struct IngestResponse: Decodable {
    let changed_files: Int?
    let skipped_files: Int?
}

@MainActor
private final class LensModel: ObservableObject {
    @Published var query = ""
    @Published var messages: [ChatMessage] = []
    @Published var health: Health?
    @Published var notice = "正在连接本地问答服务…"
    @Published var busy = false

    private let config: DesktopConfig
    private let session = URLSession(configuration: .default)
    private var conversationID: String?

    init(config: DesktopConfig) {
        self.config = config
    }

    var examplePath: String {
        URL(fileURLWithPath: config.projectRoot).appendingPathComponent("examples/corpus").path
    }

    func connect() async {
        for _ in 0..<30 {
            do {
                health = try await request("health", method: "GET", body: nil, as: Health.self)
                notice = health!.sources == 0 ? "索引为空。导入文件夹或试用示例语料。" : "已连接本地检索服务"
                if let saved = UserDefaults.standard.string(forKey: "InfraLensConversation") {
                    if let history = try? await request(
                        "conversations/\(saved)", method: "GET", body: nil,
                        as: StoredConversation.self
                    ) {
                        conversationID = saved
                        messages = history.turns.map {
                            ChatMessage(role: $0.role, content: $0.content, citations: $0.citations)
                        }
                    } else {
                        UserDefaults.standard.removeObject(forKey: "InfraLensConversation")
                    }
                }
                if health!.sources > 0 {
                    notice = "正在预热检索与回答模型…"
                    Task { await warmup() }
                }
                return
            } catch {
                try? await Task.sleep(for: .milliseconds(300))
            }
        }
        notice = "无法连接本地服务。请查看 data/desktop-backend.log。"
    }

    private func warmup() async {
        do {
            let result = try await request(
                "warmup", method: "POST", body: nil, as: WarmupResponse.self
            )
            if result.ready && notice == "正在预热检索与回答模型…" {
                notice = "检索与回答模型已就绪"
            }
        } catch {
            if notice == "正在预热检索与回答模型…" {
                notice = "预热未完成，首次提问可能较慢"
            }
        }
    }

    func ask() async {
        let text = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, !busy else { return }
        query = ""
        messages.append(ChatMessage(role: "user", content: text, citations: []))
        busy = true
        notice = "正在检索证据并生成回答…"
        defer { busy = false }
        do {
            var body: [String: Any] = ["message": text]
            if let conversationID { body["conversation_id"] = conversationID }
            let response = try await request("chat", method: "POST", body: body, as: ChatResponse.self)
            conversationID = response.conversation_id
            UserDefaults.standard.set(response.conversation_id, forKey: "InfraLensConversation")
            messages.append(ChatMessage(
                role: "assistant", content: response.answer, citations: response.citations
            ))
            notice = response.status == "answered" ? "回答已附来源" : "资料不足，请补充文档或问题"
        } catch {
            messages.append(ChatMessage(
                role: "assistant", content: "暂时无法回答：\(error.localizedDescription)", citations: []
            ))
            notice = "问答服务暂时不可用"
        }
    }

    func newConversation() {
        guard !busy else { return }
        conversationID = nil
        messages = []
        query = ""
        notice = "新对话已开始"
        UserDefaults.standard.removeObject(forKey: "InfraLensConversation")
    }

    func ingest(_ path: String) async {
        guard !busy else { return }
        busy = true
        notice = "正在导入，较大语料可能需要一些时间…"
        defer { busy = false }
        do {
            let result = try await request(
                "ingest", method: "POST", body: ["path": path, "domain": "general"],
                as: IngestResponse.self
            )
            health = try await request("health", method: "GET", body: nil, as: Health.self)
            notice = "导入完成：更新 \(result.changed_files ?? 0)，跳过 \(result.skipped_files ?? 0) 个文件"
        } catch {
            notice = error.localizedDescription
        }
    }

    private func request<T: Decodable>(
        _ path: String, method: String, body: [String: Any]?, as type: T.Type
    ) async throws -> T {
        guard let url = URL(string: "http://127.0.0.1:\(config.port)/\(path)") else {
            throw DesktopError.message("本地服务地址无效")
        }
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.timeoutInterval = path == "ingest" ? 600 :
            (path == "chat" || path == "warmup") ? 240 : 60
        if let body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw DesktopError.message("服务没有返回 HTTP 响应")
        }
        guard (200..<300).contains(http.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? "未知错误"
            throw DesktopError.message("服务错误 \(http.statusCode)：\(message)")
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
}

private struct CitationCard: View {
    let citation: ChatCitation

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("[\(citation.citation_id)] " + URL(fileURLWithPath: citation.source).lastPathComponent)
                .font(.caption.bold()).lineLimit(1)
            Text(citation.content).font(.caption).foregroundStyle(.secondary).lineLimit(3)
                .textSelection(.enabled)
            HStack {
                Text(citation.locator).font(.caption2).foregroundStyle(.secondary).lineLimit(1)
                Spacer(minLength: 4)
                Button("复制") {
                    NSPasteboard.general.clearContents()
                    NSPasteboard.general.setString(
                        "[\(citation.citation_id)] \(citation.locator)", forType: .string
                    )
                }
                .buttonStyle(.link)
                Button("打开") { NSWorkspace.shared.open(URL(fileURLWithPath: citation.source)) }
                    .buttonStyle(.link)
                    .disabled(!FileManager.default.fileExists(atPath: citation.source))
            }
        }
        .padding(9)
        .background(.quaternary.opacity(0.5), in: RoundedRectangle(cornerRadius: 9))
    }
}

private struct MessageCard: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.role == "user" { Spacer(minLength: 26) }
            VStack(alignment: .leading, spacing: 9) {
                Text(message.role == "user" ? "你" : "Infra 助手")
                    .font(.caption.bold()).foregroundStyle(.secondary)
                Text(message.content).font(.subheadline).textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                if !message.citations.isEmpty {
                    Divider()
                    Text("引用来源").font(.caption.bold()).foregroundStyle(.secondary)
                    ForEach(message.citations) { citation in CitationCard(citation: citation) }
                }
            }
            .padding(12)
            .background(message.role == "user" ? Color.accentColor.opacity(0.13) :
                        Color.primary.opacity(0.06), in: RoundedRectangle(cornerRadius: 13))
            if message.role != "user" { Spacer(minLength: 12) }
        }
    }
}

private struct LensView: View {
    @ObservedObject var model: LensModel
    @FocusState private var questionFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Image(systemName: "bubble.left.and.text.bubble.right.fill")
                    .foregroundStyle(.tint)
                Text("Infra 助手").font(.title3.bold())
                Spacer()
                Button("新对话") { model.newConversation() }
                    .disabled(model.busy)
            }
            .padding(.horizontal, 16).padding(.top, 14).padding(.bottom, 8)
            HStack {
                Text("\(model.health?.backend.uppercased() ?? "BGE") · \(model.health?.assistant?.model ?? "Ollama")")
                Spacer()
                Text("\(model.health?.sources ?? 0) 来源")
            }
            .font(.caption).foregroundStyle(.secondary)
            .padding(.horizontal, 16).padding(.bottom, 9)

            Divider()
            ScrollViewReader { proxy in
                ScrollView {
                    if model.messages.isEmpty {
                        VStack(spacing: 10) {
                            Image(systemName: "sparkles.rectangle.stack")
                                .font(.system(size: 33)).foregroundStyle(.tint)
                            Text("向知识库提问").font(.headline)
                            Text("我会查找资料、组织回答，并附上原文来源。")
                                .font(.subheadline).foregroundStyle(.secondary)
                            Button("PagedAttention 怎样管理 KV Cache？") {
                                model.query = "PagedAttention 怎样管理 KV Cache？"
                                Task { await model.ask() }
                            }
                            .buttonStyle(.link)
                        }
                        .frame(maxWidth: .infinity, minHeight: 260)
                    } else {
                        LazyVStack(spacing: 12) {
                            ForEach(model.messages) { message in MessageCard(message: message) }
                            if model.busy {
                                HStack {
                                    ProgressView().controlSize(.small)
                                    Text("正在思考…").font(.caption).foregroundStyle(.secondary)
                                    Spacer()
                                }
                                .padding(12)
                            }
                            Color.clear.frame(height: 1).id("bottom")
                        }
                        .padding(12)
                    }
                }
                .onChange(of: model.messages.count) { _, _ in
                    withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
                }
            }

            Divider()
            HStack(spacing: 8) {
                TextField("问一个 Infra 问题，或继续追问…", text: $model.query)
                    .textFieldStyle(.roundedBorder)
                    .focused($questionFocused)
                    .onSubmit { Task { await model.ask() } }
                Button("发送") { Task { await model.ask() } }
                    .disabled(model.busy || model.query.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .padding(.horizontal, 12).padding(.top, 10)
            HStack {
                Button("导入文档") { chooseSource() }.disabled(model.busy)
                if model.health?.sources == 0 {
                    Button("试用示例") { Task { await model.ingest(model.examplePath) } }
                        .disabled(model.busy)
                }
                Spacer()
                Text("本地模型 · 引用可追溯").font(.caption2).foregroundStyle(.secondary)
            }
            .padding(.horizontal, 12).padding(.top, 7)
            Text(model.notice).font(.caption).foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .lineLimit(2)
                .padding(.horizontal, 12).padding(.top, 5).padding(.bottom, 12)
        }
        .frame(minWidth: 390, minHeight: 460)
        .onAppear { questionFocused = true }
    }

    private func chooseSource() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.prompt = "导入"
        if panel.runModal() == .OK, let path = panel.url?.path {
            Task { await model.ingest(path) }
        }
    }
}

private struct OrbView: View {
    let onTap: () -> Void
    let onDrag: (NSPoint) -> Void
    let onDragEnd: () -> Void

    var body: some View {
        TimelineView(.animation(minimumInterval: 1.0 / 24.0)) { timeline in
            let scale = 1 + 0.025 * sin(timeline.date.timeIntervalSinceReferenceDate * 2.7)
            ZStack {
                Circle()
                    .fill(LinearGradient(
                        colors: [Color(red: 0.36, green: 0.81, blue: 0.98),
                                 Color(red: 0.34, green: 0.43, blue: 0.91)],
                        startPoint: .topLeading, endPoint: .bottomTrailing
                    ))
                    .overlay(Circle().stroke(.white.opacity(0.65), lineWidth: 2))
                    .shadow(color: .blue.opacity(0.4), radius: 10, y: 4)
                VStack(spacing: 5) {
                    HStack(spacing: 10) {
                        eye
                        eye
                    }
                    Capsule().fill(Color(red: 0.16, green: 0.24, blue: 0.49))
                        .frame(width: 12, height: 4)
                }
                .offset(y: 3)
                Circle().fill(.white.opacity(0.5)).frame(width: 10, height: 10)
                    .offset(x: -18, y: -20)
            }
            .frame(width: 62, height: 62)
            .scaleEffect(scale)
            .padding(11)
            .contentShape(Rectangle())
            .onTapGesture(perform: onTap)
            .simultaneousGesture(DragGesture(minimumDistance: 6)
                .onChanged { _ in onDrag(NSEvent.mouseLocation) }
                .onEnded { _ in onDragEnd() })
            .help("点击打开检索，拖动移动悬浮球")
            .accessibilityLabel("Infra Lens 悬浮球")
            .accessibilityAddTraits(.isButton)
        }
    }

    private var eye: some View {
        Ellipse().fill(.white).frame(width: 11, height: 15)
            .overlay(Circle().fill(Color(red: 0.13, green: 0.2, blue: 0.46))
                .frame(width: 5, height: 7).offset(y: 2))
    }
}

@MainActor
private final class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    private var panel: NSPanel?
    private var orb: NSPanel?
    private var orbDragOffset: NSPoint?
    private var statusItem: NSStatusItem?
    private var backend: Process?
    private var hotKeyRef: EventHotKeyRef?
    private var hotKeyHandler: EventHandlerRef?
    private var model: LensModel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        do {
            let config = try DesktopConfig.load()
            let model = LensModel(config: config)
            self.model = model
            try startBackend(config)
            Task { await model.connect() }
            let panel = NSPanel(
                contentRect: NSRect(x: 0, y: 0, width: 420, height: 500),
                styleMask: [.titled, .closable, .fullSizeContentView],
                backing: .buffered, defer: false
            )
            panel.title = "Infra Lens"
            panel.level = .floating
            panel.hidesOnDeactivate = false
            panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
            panel.isReleasedWhenClosed = false
            panel.delegate = self
            panel.contentView = NSHostingView(rootView: LensView(model: model))
            self.panel = panel
            let orb = NSPanel(
                contentRect: NSRect(x: 0, y: 0, width: 84, height: 84),
                styleMask: [.borderless], backing: .buffered, defer: false
            )
            orb.isOpaque = false
            orb.backgroundColor = .clear
            orb.hasShadow = false
            orb.level = .floating
            orb.hidesOnDeactivate = false
            orb.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
            orb.isReleasedWhenClosed = false
            orb.contentView = NSHostingView(rootView: OrbView(
                onTap: { [weak self] in self?.togglePanel() },
                onDrag: { [weak self] location in self?.dragOrb(to: location) },
                onDragEnd: { [weak self] in self?.finishOrbDrag() }
            ))
            self.orb = orb
            restoreOrbPosition()
            installMenu()
            installHotKey()
            orb.orderFrontRegardless()
        } catch {
            let alert = NSAlert()
            alert.messageText = "Infra Lens 启动失败"
            alert.informativeText = error.localizedDescription
            alert.runModal()
            NSApp.terminate(nil)
        }
    }

    func applicationWillTerminate(_ notification: Notification) {
        if let hotKeyRef { UnregisterEventHotKey(hotKeyRef) }
        if let hotKeyHandler { RemoveEventHandler(hotKeyHandler) }
        if let backend, backend.isRunning { backend.terminate() }
    }

    func windowShouldClose(_ sender: NSWindow) -> Bool {
        sender.orderOut(nil)
        return false
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows: Bool) -> Bool {
        showPanel()
        return true
    }

    private func startBackend(_ config: DesktopConfig) throws {
        let root = URL(fileURLWithPath: config.projectRoot)
        guard FileManager.default.fileExists(atPath: root.appendingPathComponent("pyproject.toml").path) else {
            throw DesktopError.message("项目目录已移动。请在新目录重新运行 build.sh。")
        }
        let executable = root.appendingPathComponent(".venv/bin/python")
        guard FileManager.default.isExecutableFile(atPath: executable.path) else {
            throw DesktopError.message("缺少 Python 环境。请在项目目录先运行 uv sync --extra dev。")
        }
        let launcher = root.appendingPathComponent("scripts/desktop_backend.py")
        guard portIsAvailable(config.port) else {
            throw DesktopError.message("本地端口 \(config.port) 已被占用。请设置 INFRA_DESKTOP_PORT 后重新构建。")
        }
        let logURL = root.appendingPathComponent("data/desktop-backend.log")
        try FileManager.default.createDirectory(at: logURL.deletingLastPathComponent(),
                                                withIntermediateDirectories: true)
        FileManager.default.createFile(atPath: logURL.path, contents: nil)
        let log = try FileHandle(forWritingTo: logURL)
        try log.seekToEnd()
        let process = Process()
        process.executableURL = executable
        process.currentDirectoryURL = root
        var arguments = [
            launcher.path, "--parent-pid", String(ProcessInfo.processInfo.processIdentifier),
            "--backend", config.backend, "--index", config.indexDirectory,
            "--port", String(config.port)
        ]
        if config.rerank { arguments.append("--rerank") }
        process.arguments = arguments
        process.standardOutput = log
        process.standardError = log
        try process.run()
        backend = process
    }

    private func portIsAvailable(_ port: Int) -> Bool {
        guard (1...65535).contains(port) else { return false }
        let descriptor = socket(AF_INET, SOCK_STREAM, 0)
        guard descriptor >= 0 else { return false }
        defer { close(descriptor) }
        var address = sockaddr_in()
        address.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)
        address.sin_family = sa_family_t(AF_INET)
        address.sin_port = UInt16(port).bigEndian
        inet_pton(AF_INET, "127.0.0.1", &address.sin_addr)
        return withUnsafePointer(to: &address) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.bind(descriptor, $0, socklen_t(MemoryLayout<sockaddr_in>.size)) == 0
            }
        }
    }

    private func installMenu() {
        let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        item.button?.image = NSImage(systemSymbolName: "square.stack.3d.up.magnifyingglass",
                                     accessibilityDescription: "Infra Lens")
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "显示 / 隐藏检索面板", action: #selector(togglePanelAction),
                                keyEquivalent: ""))
        menu.addItem(.separator())
        menu.addItem(NSMenuItem(title: "退出 Infra Lens", action: #selector(quit),
                                keyEquivalent: "q"))
        for entry in menu.items { entry.target = self }
        item.menu = menu
        statusItem = item
    }

    private func installHotKey() {
        let identifier = EventHotKeyID(signature: 0x494E4652, id: 1)
        let status = RegisterEventHotKey(UInt32(kVK_Space), UInt32(controlKey | optionKey),
                                         identifier, GetApplicationEventTarget(), 0, &hotKeyRef)
        guard status == noErr else {
            model?.notice = "快捷键已被占用，请用菜单栏图标打开悬浮窗。"
            return
        }
        var eventType = EventTypeSpec(eventClass: OSType(kEventClassKeyboard),
                                      eventKind: UInt32(kEventHotKeyPressed))
        InstallEventHandler(GetApplicationEventTarget(), { _, _, context in
            guard let context else { return OSStatus(eventNotHandledErr) }
            let app = Unmanaged<AppDelegate>.fromOpaque(context).takeUnretainedValue()
            Task { @MainActor in app.togglePanel() }
            return noErr
        }, 1, &eventType, Unmanaged.passUnretained(self).toOpaque(), &hotKeyHandler)
    }

    private func showPanel() {
        positionPanelNearOrb()
        NSApp.activate(ignoringOtherApps: true)
        panel?.makeKeyAndOrderFront(nil)
        panel?.orderFrontRegardless()
    }

    private func togglePanel() {
        if panel?.isVisible == true { panel?.orderOut(nil) } else { showPanel() }
    }

    private func restoreOrbPosition() {
        guard let orb else { return }
        let visible = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1000, height: 700)
        let defaults = UserDefaults.standard
        let saved = defaults.object(forKey: "InfraLensOrbX") != nil
        let x = saved ? defaults.double(forKey: "InfraLensOrbX") : visible.maxX - 104
        let y = saved ? defaults.double(forKey: "InfraLensOrbY") : visible.minY + 120
        orb.setFrameOrigin(NSPoint(
            x: min(max(x, visible.minX + 8), visible.maxX - 92),
            y: min(max(y, visible.minY + 8), visible.maxY - 92)
        ))
    }

    private func dragOrb(to pointer: NSPoint) {
        guard let orb else { return }
        if orbDragOffset == nil {
            orbDragOffset = NSPoint(x: pointer.x - orb.frame.minX, y: pointer.y - orb.frame.minY)
        }
        guard let offset = orbDragOffset else { return }
        let visible = NSScreen.screens.first(where: { $0.frame.contains(pointer) })?.visibleFrame
            ?? NSScreen.main?.visibleFrame ?? orb.frame
        let x = min(max(pointer.x - offset.x, visible.minX + 8), visible.maxX - orb.frame.width - 8)
        let y = min(max(pointer.y - offset.y, visible.minY + 8), visible.maxY - orb.frame.height - 8)
        orb.setFrameOrigin(NSPoint(x: x, y: y))
        if panel?.isVisible == true { positionPanelNearOrb() }
    }

    private func finishOrbDrag() {
        guard let orb else { return }
        orbDragOffset = nil
        UserDefaults.standard.set(Double(orb.frame.minX), forKey: "InfraLensOrbX")
        UserDefaults.standard.set(Double(orb.frame.minY), forKey: "InfraLensOrbY")
    }

    private func positionPanelNearOrb() {
        guard let panel, let orb else { return }
        let visible = NSScreen.screens.first(where: { $0.frame.intersects(orb.frame) })?.visibleFrame
            ?? NSScreen.main?.visibleFrame ?? orb.frame
        let left = orb.frame.minX - panel.frame.width - 12
        let preferredX = left >= visible.minX + 8 ? left : orb.frame.maxX + 12
        let x = min(max(preferredX, visible.minX + 8), visible.maxX - panel.frame.width - 8)
        let y = min(max(orb.frame.midY - panel.frame.height / 2, visible.minY + 8),
                    visible.maxY - panel.frame.height - 8)
        panel.setFrameOrigin(NSPoint(x: x, y: y))
    }

    @objc private func togglePanelAction() { togglePanel() }
    @objc private func quit() { NSApp.terminate(nil) }
}

@main
private struct InfraLensApp {
    static func main() {
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.run()
    }
}
