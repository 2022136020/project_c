import 'package:flutter/material.dart';
import '../../models/account.dart';
import '../../models/transaction.dart';
import '../../services/firestore_service.dart';
import 'add_transaction_screen.dart';

class AccountDetailScreen extends StatelessWidget {
  final Account account;
  const AccountDetailScreen({super.key, required this.account});

  @override
  Widget build(BuildContext context) {
    final service = FirestoreService();

    return Scaffold(
      appBar: AppBar(
        title: Text(account.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (_) => AlertDialog(
                  title: const Text('계좌 삭제'),
                  content: Text('${account.name}을(를) 삭제할까요?'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false),
                        child: const Text('취소')),
                    TextButton(onPressed: () => Navigator.pop(context, true),
                        child: const Text('삭제', style: TextStyle(color: Colors.red))),
                  ],
                ),
              );
              if (ok == true) {
                await service.deleteAccount(account.id);
                if (context.mounted) Navigator.pop(context);
              }
            },
          ),
        ],
      ),
      body: StreamBuilder<List<AccountTransaction>>(
        stream: service.transactionsStream(account.id),
        builder: (context, snapshot) {
          final txs = snapshot.data ?? [];

          double balance = account.initialBalance;
          for (final tx in txs) {
            balance += tx.type == 'deposit' ? tx.amount : -tx.amount;
          }

          return Column(
            children: [
              _BalanceCard(
                  initialBalance: account.initialBalance,
                  currentBalance: balance,
                  type: account.type),
              const Divider(height: 1),
              Expanded(
                child: txs.isEmpty
                    ? const Center(child: Text('입출금 내역이 없습니다.'))
                    : ListView.builder(
                        itemCount: txs.length,
                        itemBuilder: (_, i) => _TxTile(tx: txs[i]),
                      ),
              ),
            ],
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(
              builder: (_) => AddTransactionScreen(accountId: account.id)),
        ),
        icon: const Icon(Icons.add),
        label: const Text('입출금'),
      ),
    );
  }
}

class _BalanceCard extends StatelessWidget {
  final double initialBalance;
  final double currentBalance;
  final String type;
  const _BalanceCard(
      {required this.initialBalance,
      required this.currentBalance,
      required this.type});

  @override
  Widget build(BuildContext context) {
    final diff = currentBalance - initialBalance;
    final color = diff >= 0 ? Colors.blue : Colors.red;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(type == 'stock' ? Icons.bar_chart : Icons.currency_bitcoin,
                size: 16, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 4),
            Text(type == 'stock' ? '주식' : '코인',
                style: TextStyle(
                    color: Theme.of(context).colorScheme.primary,
                    fontSize: 12)),
          ]),
          const SizedBox(height: 8),
          Text(
            '₩${_fmt(currentBalance)}',
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            '${diff >= 0 ? '+' : ''}₩${_fmt(diff)} (초기 ₩${_fmt(initialBalance)})',
            style: TextStyle(color: color, fontSize: 13),
          ),
        ],
      ),
    );
  }

  String _fmt(double v) => v.abs().toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

class _TxTile extends StatelessWidget {
  final AccountTransaction tx;
  const _TxTile({required this.tx});

  @override
  Widget build(BuildContext context) {
    final isDeposit = tx.type == 'deposit';
    return ListTile(
      leading: CircleAvatar(
        backgroundColor:
            isDeposit ? Colors.blue.shade50 : Colors.red.shade50,
        child: Icon(
          isDeposit ? Icons.arrow_downward : Icons.arrow_upward,
          color: isDeposit ? Colors.blue : Colors.red,
          size: 18,
        ),
      ),
      title: Text(
        '${isDeposit ? '+' : '-'}₩${tx.amount.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')}',
        style: TextStyle(
          fontWeight: FontWeight.w600,
          color: isDeposit ? Colors.blue : Colors.red,
        ),
      ),
      subtitle: Text(tx.note ?? (isDeposit ? '입금' : '출금')),
      trailing: Text(
        '${tx.date.year}.${tx.date.month.toString().padLeft(2, '0')}.${tx.date.day.toString().padLeft(2, '0')}',
        style: const TextStyle(fontSize: 12, color: Colors.grey),
      ),
    );
  }
}
