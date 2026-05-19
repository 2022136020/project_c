import 'package:flutter/material.dart';
import '../models/account.dart';
import '../services/auth_service.dart';
import '../services/firestore_service.dart';
import 'account/account_detail_screen.dart';
import 'account/add_account_screen.dart';
import 'position/position_list_screen.dart';
import 'chart/chart_screen.dart';
import 'dashboard/dashboard_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tabIndex = 0;
  final _authService = AuthService();
  final _firestoreService = FirestoreService();

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<List<Account>>(
      stream: _firestoreService.accountsStream(),
      builder: (context, snapshot) {
        final accounts = snapshot.data ?? [];

        return Scaffold(
          appBar: AppBar(
            title: const Text('Portfolio Tracker'),
            actions: [
              IconButton(
                icon: const Icon(Icons.logout),
                tooltip: '로그아웃',
                onPressed: () => _authService.signOut(),
              ),
            ],
          ),
          body: [
            DashboardScreen(accounts: accounts),
            _AccountsTab(accounts: accounts),
            PositionListScreen(accounts: accounts),
            const ChartScreen(),
          ][_tabIndex],
          bottomNavigationBar: NavigationBar(
            selectedIndex: _tabIndex,
            onDestinationSelected: (i) => setState(() => _tabIndex = i),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home),
                  label: '홈'),
              NavigationDestination(
                  icon: Icon(Icons.account_balance_outlined),
                  selectedIcon: Icon(Icons.account_balance),
                  label: '계좌'),
              NavigationDestination(
                  icon: Icon(Icons.trending_up_outlined),
                  selectedIcon: Icon(Icons.trending_up),
                  label: '포지션'),
              NavigationDestination(
                  icon: Icon(Icons.bar_chart_outlined),
                  selectedIcon: Icon(Icons.bar_chart),
                  label: '차트'),
            ],
          ),
        );
      },
    );
  }
}

class _AccountsTab extends StatelessWidget {
  final List<Account> accounts;
  const _AccountsTab({required this.accounts});

  @override
  Widget build(BuildContext context) {
    if (accounts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.account_balance_outlined,
                size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('계좌가 없습니다.',
                style: TextStyle(fontSize: 16, color: Colors.grey)),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: () => Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const AddAccountScreen())),
              icon: const Icon(Icons.add),
              label: const Text('계좌 등록'),
            ),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        ...accounts.map((a) => _AccountCard(account: a)),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const AddAccountScreen())),
          icon: const Icon(Icons.add),
          label: const Text('계좌 추가'),
        ),
      ],
    );
  }
}

class _AccountCard extends StatelessWidget {
  final Account account;
  const _AccountCard({required this.account});

  @override
  Widget build(BuildContext context) {
    final service = FirestoreService();

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(
              builder: (_) => AccountDetailScreen(account: account)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(
                backgroundColor: account.type == 'stock'
                    ? Colors.indigo.shade50
                    : Colors.orange.shade50,
                child: Icon(
                  account.type == 'stock'
                      ? Icons.bar_chart
                      : Icons.currency_bitcoin,
                  color: account.type == 'stock'
                      ? Colors.indigo
                      : Colors.orange,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(account.name,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 15)),
                    Text(account.type == 'stock' ? '주식' : '코인',
                        style: const TextStyle(
                            color: Colors.grey, fontSize: 12)),
                  ],
                ),
              ),
              FutureBuilder<double>(
                future: service.calcBalance(
                    account.id, account.initialBalance),
                builder: (_, snap) => Text(
                  snap.hasData
                      ? '₩${snap.data!.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')}'
                      : '...',
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 15),
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }
}
